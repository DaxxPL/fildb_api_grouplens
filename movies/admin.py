from django.contrib import admin
from .models import Movie, Genre, Rating, User, Tag, TimeTag, Link

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Rating)
admin.site.register(User)
admin.site.register(Tag)
admin.site.register(TimeTag)
admin.site.register(Link)
