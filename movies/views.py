from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
from .models import Movie, Genre, Rating, User, Tag, Link, TimeTag
from .serializers import ListMovieSerializer, DetailMovieSerializer, ListTagSerializer, DetailTagSerializer, \
    ListUserSerializer, ListRatingSerializer, DetailRatingSerializer, ListGenreSerializer, DetailGenreSerializer, \
    ListLinkSerializer, DetailLinkSerializer, CreateUserSerializer, CreateMovieSerializer, CreateTagSerializer, \
    CreateRatingSerializer, CreateGenreSerializer, CreateLinkSerializer, DetailUserSerializer
from rest_framework.views import APIView
from urllib.error import URLError
import zipfile
from io import BytesIO
import csv
import re
import datetime
import pytz
import django_filters
from django.db import models
import codecs
import requests

YEAR_PATTERN = r"\(\d{4}\)\s*$"
LOCKED_FROM_EXTERNAL_API = False


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

    @staticmethod
    def fetch_from_url(source):
        return requests.get('http://files.grouplens.org/datasets/movielens/%s.zip' % source, stream=True)

    def post(self, request):
        global LOCKED_FROM_EXTERNAL_API, YEAR_PATTERN
        if LOCKED_FROM_EXTERNAL_API is False:
            LOCKED_FROM_EXTERNAL_API = True
            try:
                source = request.data['source']
            except KeyError:
                LOCKED_FROM_EXTERNAL_API = False
                return Response('no source data in body',
                                status=status.HTTP_400_BAD_REQUEST)
            if source in settings.AVAILABLE_SOURCES:
                try:
                    response = self.fetch_from_url(request.data['source'])
                except URLError:
                    LOCKED_FROM_EXTERNAL_API = False
                    return Response("External server respond time out",
                                    status=status.HTTP_504_GATEWAY_TIMEOUT)
                try:
                    zip_file = zipfile.ZipFile(BytesIO(response.content), allowZip64=True)
                except (zipfile.BadZipFile, TypeError, AttributeError):
                    LOCKED_FROM_EXTERNAL_API = False
                    return Response("External server provided wrong file",
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                try:
                    file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                                      settings.FILES_TO_IMPORT['movies']), 'utf-8'))
                except (csv.Error, KeyError):
                    LOCKED_FROM_EXTERNAL_API = False
                    return Response("Failed to read CSV file",
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                for line in file:
                    if file.line_num != 1:
                        movie = Movie()
                        movie.id = int(line[0])
                        try:
                            movie.year = re.findall(YEAR_PATTERN, line[1])[0].strip()[1:-1]
                        except IndexError:
                            pass
                        movie.title = re.sub(YEAR_PATTERN, '', line[1]).strip()
                        movie.save()
                        for item in line[2].split('|'):
                            genre = Genre.objects.get_or_create(name=item)[0]
                            movie.genres.add(genre)
                        movie.save()
                    elif line != ['movieId', 'title', 'genres']:
                        LOCKED_FROM_EXTERNAL_API = False
                        return Response('File contains wrong headers!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        Movie.objects.all().delete()
                try:
                    file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                                      settings.FILES_TO_IMPORT['ratings']), 'utf-8'))
                except csv.Error:
                    LOCKED_FROM_EXTERNAL_API = False
                    return Response("Failed to read CSV file",
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                for line in file:
                    if file.line_num != 1:
                        rating = Rating()
                        user = User.objects.get_or_create(id=line[0])[0]
                        rating.user = user
                        try:
                            rating.movie = Movie.objects.get(id=line[1])
                        except Movie.DoesNotExist:
                            continue
                        rating.score = float(line[2])
                        rating.date = datetime.datetime.fromtimestamp(int(line[3]), tz=pytz.UTC)
                        rating.save()
                    elif line != ['userId', 'movieId', 'rating', 'timestamp']:
                        LOCKED_FROM_EXTERNAL_API = False
                        return Response('File contains wrong headers!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        Rating.objects.all().delete()
                try:
                    file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                                      settings.FILES_TO_IMPORT['tags']), 'utf-8'))
                except csv.Error:
                    LOCKED_FROM_EXTERNAL_API = False
                    return Response("Failed to read CSV file",
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                for line in file:
                    if file.line_num != 1:
                        tag = Tag.objects.get_or_create(name=line[2].lower().strip())[0]
                        timetag = TimeTag()
                        timetag.tag = tag
                        user = User.objects.get_or_create(id=line[0])[0]
                        tag.users.add(user)
                        timetag.user = user
                        try:
                            tag.movies.add(Movie.objects.get(id=line[1]))
                            timetag.movie = Movie.objects.get(id=line[1])
                        except Movie.DoesNotExist:
                            continue
                        timetag.date = datetime.datetime.fromtimestamp(int(line[3]), tz=pytz.UTC)
                        tag.save()
                        timetag.save()
                    elif line != ['userId', 'movieId', 'tag', 'timestamp']:
                        LOCKED_FROM_EXTERNAL_API = False
                        return Response('File contains wrong headers!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        Tag.objects.all().delete()
                        TimeTag.objects.all().delete()
                try:
                    file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                                      settings.FILES_TO_IMPORT['links']), 'utf-8'))
                except csv.Error:
                    LOCKED_FROM_EXTERNAL_API = False
                    return Response("Failed to read CSV file",
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                for line in file:
                    if file.line_num != 1:
                        link = Link()
                        try:
                            link.movie = Movie.objects.get(id=line[0])
                        except Movie.DoesNotExist:
                            continue
                        link.movie_lens = 'https://movielens.org/movies/%s' % line[0]
                        link.imdb = 'https://imdb.com/title/tt%s' % line[1]
                        link.tmdb = 'https://www.themoviedb.org/movie/%s' % line[2]
                        link.save()
                    elif line != ['movieId', 'imdbId', 'tmdbId']:
                        LOCKED_FROM_EXTERNAL_API = False
                        return Response('File contains wrong headers!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        Link.objects.all().delete()
                LOCKED_FROM_EXTERNAL_API = False
                return Response("Success!")
            else:
                LOCKED_FROM_EXTERNAL_API = False
                return Response('This source is not available', status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Another POST /db executing. Statement locked!",
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
