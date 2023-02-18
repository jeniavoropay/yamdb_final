from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, CustomUser, Genre, Review, Title
from reviews.validators import (regex_validator, reserved_names_validator,
                                validate_year)


class SignupSerializer(serializers.Serializer):
    """Проверка username и email перед выдачей confirmation_code."""
    username = serializers.CharField(
        max_length=settings.USERNAME_LENGHT,
        required=True,
        validators=[regex_validator, reserved_names_validator]
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_LENGHT,
        required=True
    )


class TokenSerializer(serializers.Serializer):
    """Проверка username и confirmation_code перед выдачей токена."""
    username = serializers.CharField(
        max_length=settings.USERNAME_LENGHT,
        required=True,
        validators=[regex_validator, reserved_names_validator]
    )
    confirmation_code = serializers.CharField(
        required=True
    )


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы администратора с пользователями."""

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_username(self, value):
        regex_validator(value)
        reserved_names_validator(value)
        return value


class UserSerializer(AdminUserSerializer):
    """Сериализатор работы пользователей с собственным профилем."""

    class Meta(AdminUserSerializer.Meta):
        read_only_fields = ('role',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализует и десериализует данные модели Genre.
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализует и десериализует данные модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализует данные модели Title."""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'description',
            'rating',
            'category'
        )
        read_only_fields = fields


class TitlePostPatchSerializer(serializers.ModelSerializer):
    """Десериализует данные модели Title."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )
        read_only_true = ('rating',)

    def validate_year(self, value):
        validate_year(value)
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    score = serializers.IntegerField(
        validators=(
            MinValueValidator(settings.MIN_SCORE),
            MaxValueValidator(settings.MAX_SCORE)
        )
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        if Review.objects.filter(
            title=get_object_or_404(
                Title, pk=request.parser_context['kwargs'].get('title_id')
            ), author=request.user
        ).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализует и десериализует данные модели Comment."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
