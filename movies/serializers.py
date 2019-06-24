from rest_framework import serializers
from .models import Movie, Tag, User, Rating, Genre, Link


class DetailLinkSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField(many=False, read_only=False)

    class Meta:
        model = Link
        fields = '__all__'


class ListLinkSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField(many=False, read_only=False)
    link = serializers.HyperlinkedIdentityField(view_name='link-detail', format='html')

    class Meta:
        model = Link
        fields = '__all__'


class CreateLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = '__all__'


class NestedMovieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = ('pk', )


class DetailGenreSerializer(serializers.ModelSerializer):
    movies = NestedMovieSerializer(many=True)

    class Meta:
        model = Genre
        fields = '__all__'


class ListGenreSerializer(serializers.ModelSerializer):
    movies = serializers.StringRelatedField(many=True, read_only=False)
    link = serializers.HyperlinkedIdentityField(view_name='genre-detail', format='html')

    class Meta:
        model = Genre
        fields = ('name', 'link', 'movies')


class CreateGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'


class DetailRatingSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField(many=False)

    class Meta:
        model = Rating
        fields = '__all__'


class ListRatingSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField(many=False, read_only=False)
    link = serializers.HyperlinkedIdentityField(view_name='rating-detail', lookup_field='pk', format='html')

    class Meta:
        model = Rating
        fields = ('movie', 'score', 'date', 'user', 'link')


class CreateRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = '__all__'


class NestedLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = ('imdb', )


class DetailMovieSerializer(serializers.ModelSerializer):

    link = NestedLinkSerializer(many=False)
    score = serializers.SerializerMethodField()

    def get_score(self, obj):
        return obj.score

    class Meta:
        model = Movie
        fields = ['title', 'score', 'genres', 'tag', 'link', 'year']


class ListMovieSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(view_name='movie-detail', lookup_field='pk', format='html')
    tag = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'year', 'link', 'tag']


class CreateMovieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = ['pk', 'title', 'year', 'genres']


class DetailTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class ListTagSerializer(serializers.ModelSerializer):
    movies = serializers.StringRelatedField(many=True)
    link = serializers.HyperlinkedIdentityField(view_name='tag-detail', lookup_field='pk', format='html')

    class Meta:
        model = Tag
        fields = '__all__'


class CreateTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class ListUserSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='pk', format='html')

    class Meta:
        model = User
        fields = '__all__'


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class NestedTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('pk', )


class NestedRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ('pk', )


class DetailUserSerializer(serializers.ModelSerializer):
    tag = NestedTagSerializer(many=True)
    ratings = NestedRatingSerializer(many=True)

    class Meta:
        model = User
        fields = '__all__'


