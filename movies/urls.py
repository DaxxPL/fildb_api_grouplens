from django.urls import path
from .views import ListMoviesView, FetchFromExternalApi, DetailMoviesView, ListTagView, DetailTagView, ListUsersView, \
    ListRatingView, DetailRatingView, ListGenreView, DetailGenreView, ListLinkView, DetailLinkView, CreateUserView,\
    CreateMoviesView, CreateTagView, CreateRatingView, CreateGenreView, CreateLinkView, DetailUsersView
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='API')

urlpatterns = [
    path('', schema_view),
    path('movies/', ListMoviesView.as_view(), name='movies'),
    path('movies/create/', CreateMoviesView.as_view(), name='movie-create'),
    path('movies/<int:pk>/', DetailMoviesView.as_view(), name='movie-detail'),
    path('db/', FetchFromExternalApi.as_view(), name='db'),
    path('tags/', ListTagView.as_view(), name='tags'),
    path('tags/create/', CreateTagView.as_view(), name='tag-create'),
    path('tags/<str:pk>/', DetailTagView.as_view(), name='tag-detail'),
    path('users/', ListUsersView.as_view(), name='users'),
    path('users/<int:pk>/', DetailUsersView.as_view(), name='user-detail'),
    path('users/create/', CreateUserView.as_view(), name='user-create'),
    path('ratings/', ListRatingView.as_view(), name='ratings'),
    path('ratings/create/', CreateRatingView.as_view(), name='rating-create'),
    path('ratings/<int:pk>/', DetailRatingView.as_view(), name='rating-detail'),
    path('genres/', ListGenreView.as_view(), name='genres'),
    path('genres/create/', CreateGenreView.as_view(), name='genre-create'),
    path('genres/<str:pk>/', DetailGenreView.as_view(), name='genre-detail'),
    path('links/', ListLinkView.as_view(), name='links'),
    path('links/create/', CreateLinkView.as_view(), name='link-create'),
    path('links/<str:pk>/', DetailLinkView.as_view(), name='link-detail'),
]
