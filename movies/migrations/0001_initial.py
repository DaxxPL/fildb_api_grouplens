# Generated by Django 2.2.2 on 2019-06-26 10:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('year', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('movie', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='link', serialize=False, to='movies.Movie')),
                ('movie_lens', models.URLField()),
                ('imdb', models.URLField()),
                ('tmdb', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('movies', models.ManyToManyField(related_name='tag', to='movies.Movie')),
                ('users', models.ManyToManyField(related_name='tag', to='movies.User')),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('movies', models.ManyToManyField(related_name='genres', to='movies.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='TimeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.Movie')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.Tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.User')),
            ],
            options={
                'unique_together': {('date', 'user', 'tag', 'movie')},
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.Movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='movies.User')),
            ],
            options={
                'unique_together': {('user', 'movie')},
            },
        ),
    ]
