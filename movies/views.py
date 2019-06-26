from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
from .models import Movie, Genre, Rating, User, Tag, Link, TimeTag
from .serializers import ListMovieSerializer, DetailMovieSerializer, ListTagSerializer, DetailTagSerializer, \
    ListUserSerializer, ListRatingSerializer, DetailRatingSerializer, ListGenreSerializer, DetailGenreSerializer, \
    ListLinkSerializer, DetailLinkSerializer, CreateUserSerializer, CreateMovieSerializer, CreateTagSerializer, \
    CreateRatingSerializer, CreateGenreSerializer, CreateLinkSerializer, DetailUserSerializer
from rest_framework.views import APIView
import django_filters
from django.db import models
from .tasks import parse_from_url_to_db
from fimdb_api_grouplens.celery import app
from django_celery_results.models import TaskResult

YEAR_PATTERN = r"\(\d{4}\)\s*$"


class ListMoviesFilter(django_filters.FilterSet):
    tag = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        conjoined=True,
    )
    year = django_filters.NumberFilter(field_name='year')

    sort = django_filters.OrderingFilter(
        fields=(
            ('year', 'year')
        )
    )

    class Meta:
        model = Movie
        fields = ['year']


class ListLinkView(generics.ListAPIView):
    models = Link
    queryset = Link.objects.all()
    serializer_class = ListLinkSerializer


class DetailLinkView(generics.RetrieveUpdateDestroyAPIView):
    models = Link
    serializer_class = DetailLinkSerializer
    queryset = Link.objects.all()


class CreateLinkView(generics.CreateAPIView):
    models = Link
    serializer_class = CreateLinkSerializer


class ListGenreView(generics.ListAPIView):
    models = Genre
    queryset = Genre.objects.all()
    serializer_class = ListGenreSerializer


class DetailGenreView(generics.RetrieveUpdateDestroyAPIView):
    models = Genre
    serializer_class = DetailGenreSerializer
    queryset = Genre.objects.all()


class CreateGenreView(generics.CreateAPIView):
    models = Genre
    serializer_class = CreateGenreSerializer


class ListRatingView(generics.ListAPIView):
    models = Rating
    queryset = Rating.objects.all()
    serializer_class = ListRatingSerializer


class DetailRatingView(generics.RetrieveUpdateDestroyAPIView):
    models = Rating
    serializer_class = DetailRatingSerializer
    queryset = Rating.objects.all()


class CreateRatingView(generics.CreateAPIView):
    models = Rating
    serializer_class = CreateRatingSerializer


class ListUsersView(generics.ListAPIView):
    models = User
    queryset = User.objects.all()
    serializer_class = ListUserSerializer


class DetailUsersView(generics.RetrieveUpdateDestroyAPIView):
    models = User
    serializer_class = DetailUserSerializer
    queryset = User.objects.all()


class CreateUserView(generics.CreateAPIView):
    models = User
    serializer_class = CreateUserSerializer


class ListTagView(generics.ListAPIView):
    models = Tag
    queryset = Tag.objects.all()
    serializer_class = ListTagSerializer


class DetailTagView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = DetailTagSerializer


class CreateTagView(generics.CreateAPIView):
    models = Tag
    serializer_class = CreateTagSerializer


class ListMoviesView(generics.ListAPIView):
    model = Movie
    queryset = Movie.objects.all()
    serializer_class = ListMovieSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ListMoviesFilter


class DetailMoviesView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = DetailMovieSerializer

    def get_queryset(self):
        class Round(models.Func):
            function = 'ROUND'
            template = '%(function)s(%(expressions)s, 2)'

        queryset = super().get_queryset().annotate(score=Round(models.Avg('rating__score')))
        return queryset


class CreateMoviesView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = CreateMovieSerializer


class FetchFromExternalApi(APIView):

    def post(self, request):
        try:
            source = request.data['source']
        except KeyError:
            return Response('no source data in body',
                            status=status.HTTP_400_BAD_REQUEST)
        name = list(app.control.inspect().active().keys())[0]
        if len(list(filter(lambda x: x == parse_from_url_to_db.__name__,
                           [i['name'] for i in app.control.inspect().active()[name]]))) >= 1:
            return Response('another /db/[post] executing now', status=status.HTTP_429_TOO_MANY_REQUESTS)
        parse_from_url_to_db.delay(source)
        return Response('request initalized, to chceck status of request sent get for this url',
                        status=status.HTTP_202_ACCEPTED)

    def get(self, request):
        try:
            result = TaskResult.objects.get(status='STARTED')
        except TaskResult.DoesNotExist:
            result = TaskResult.objects.order_by('-date_done').first()
        return Response({
            'status': result.status,
            'info': result.result,
            'started': result.date_done
        }, status=status.HTTP_200_OK)

