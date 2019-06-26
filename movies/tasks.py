from __future__ import absolute_import, unicode_literals
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from .models import Movie, Genre, Rating, User, Tag, Link, TimeTag
from urllib.error import URLError
import zipfile
from io import BytesIO
import csv
import re
import datetime
import pytz
import codecs
import requests
import celery
from celery import states
from celery.utils.log import get_task_logger
from fimdb_api_grouplens.celery import app

YEAR_PATTERN = r"\(\d{4}\)\s*$"
logger = get_task_logger(__name__)


def fetch_from_url(source):
    return requests.get('http://files.grouplens.org/datasets/movielens/%s.zip' % source, stream=True, timeout=1)


@celery.task(name="parse_from_url_to_db")
def parse_from_url_to_db(source):
    global YEAR_PATTERN
    celery.current_task.update_state(state=states.STARTED, meta={'progress': 'downloading file'})
    if source in settings.AVAILABLE_SOURCES:
        response = fetch_from_url(source)
        zip_file = zipfile.ZipFile(BytesIO(response.content), allowZip64=True)
        file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                              settings.FILES_TO_IMPORT['movies']), 'utf-8'))
        celery.current_task.update_state(state=states.STARTED, meta={'progress': 'downloading movies'})
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
                raise ImportError('File contains wrong headers!')
            else:
                Movie.objects.all().delete()
        file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                          settings.FILES_TO_IMPORT['ratings']), 'utf-8'))
        celery.current_task.update_state(state=states.STARTED, meta={'progress': 'downloading ratings'})
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
                raise ImportError('File contains wrong headers!')
            else:
                Rating.objects.all().delete()

        file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                          settings.FILES_TO_IMPORT['tags']), 'utf-8'))
        celery.current_task.update_state(state=states.STARTED, meta={'progress': 'downloading tags'})
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
                raise ImportError('File contains wrong headers!')
            else:
                Tag.objects.all().delete()
                TimeTag.objects.all().delete()
        file = csv.reader(codecs.iterdecode(zip_file.open(source + '/' +
                                                          settings.FILES_TO_IMPORT['links']), 'utf-8'))
        celery.current_task.update_state(state=states.STARTED, meta={'progress': 'downloading links'})
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
                return Response('File contains wrong headers!', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                Link.objects.all().delete()
        return "Success!"
    else:
        raise AttributeError('This source is not available')
