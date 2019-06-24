from django.db import models
from django.utils.timezone import now


class Movie(models.Model):
    title = models.CharField(max_length=255, null=False)
    year = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.title


class Genre(models.Model):
    name = models.CharField(max_length=255, null=False, primary_key=True)
    movies = models.ManyToManyField(Movie, related_name='genres')

    def __str__(self):
        return self.name


class User(models.Model):
    id = models.PositiveIntegerField(primary_key=True, null=False)

    def __str__(self):
        return 'User Id: %s' % self.id


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField()
    date = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return '%1.1f - %s' % (self.score, self.movie)


class Tag(models.Model):
    users = models.ManyToManyField(User, related_name='tag')
    movies = models.ManyToManyField(Movie, related_name='tag')
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name


class TimeTag(models.Model):
    date = models.DateTimeField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('date', 'user', 'tag', 'movie')

    def __str__(self):
        return self.date.__str__() + self.user.__str__() + self.tag.__str__() + self.movie.__str__()


class Link(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, primary_key=True, related_name='link')
    movie_lens = models.URLField()
    imdb = models.URLField()
    tmdb = models.URLField()
