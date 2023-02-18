from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import (regex_validator, reserved_names_validator,
                         validate_year)

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class CustomUser(AbstractUser):
    """Кастомная модель User."""
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.USERNAME_LENGHT,
        unique=True,
        validators=[regex_validator, reserved_names_validator],
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=settings.EMAIL_LENGHT,
        unique=True
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLES,
        max_length=max(len(role) for role, _ in ROLES),
        default=USER
    )

    class Meta(AbstractUser.Meta):
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class GenreCategory(models.Model):
    """Базовый класс для категорий и жанров."""
    name = models.CharField(
        max_length=settings.NAME_LENGHT,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=settings.SLUG_LENGHT,
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(GenreCategory):
    """Модель жанров."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(GenreCategory):
    """Модель категорий."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(
        max_length=settings.NAME_LENGHT,
        verbose_name='Название',
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанры'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель для связи произведений и жанров."""
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Жанры + Произведения'

    def __str__(self):
        return f'{self.genre} — {self.title}'


class ReviewComment(models.Model):
    """Базовый класс для отзывов и комментариев."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:50]


class Review(ReviewComment):
    """Модель отзывов."""
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(settings.MIN_SCORE),
            MaxValueValidator(settings.MAX_SCORE)
        ],
        verbose_name='Оценка'
    )

    class Meta(ReviewComment.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(ReviewComment):
    """Модель комментариев."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    class Meta(ReviewComment.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
