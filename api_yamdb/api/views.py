from django.db.models import Avg
from django.db import IntegrityError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, CustomUser
from .permissions import (
    AdminPermission,
    IsAdminOrReadOnlyPermission,
    IsStaffOrAuthorOrReadOnlyPermission
)
from .serializers import (
    SignupSerializer,
    TokenSerializer,
    UserSerializer,
    AdminUserSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitlePostPatchSerializer,
    TitleSerializer,
)
from .filters import TitlesFilter


class SignUpView(APIView):
    """
    При получении POST-запроса с параметрами email и username
    отправляет письмо с кодом подтверждения (confirmation_code)
    на указанный адрес email.
    """
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = CustomUser.objects.get_or_create(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username']
            )
        except IntegrityError:
            return Response(
                'Такой username или email уже существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        confirmation_code = default_token_generator.make_token(user)
        to_email = serializer.validated_data['email']
        send_mail(
            'Вы зарегистрировались на сайте YaMDb',
            f'Ваш код подтверждения: {confirmation_code}.',
            settings.YAMDB_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    """
    Генерация и отправка токена пользователю.
    """
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(CustomUser, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            access_token = RefreshToken.for_user(user).access_token
            data = {'token': str(access_token)}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(
            'Неверный код подтверждения.',
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    Реализует операции с моделью CustomUser:
    - получения списка пользователей;
    - создание пользователя;
    - получение детализации по пользователю;
    - редактирование поьзователя;
    - удаление пользователя.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (AdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        ['GET', 'PATCH'],
        url_path='me',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(
                UserSerializer(request.user).data, status=status.HTTP_200_OK
            )
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitlesViewSet(viewsets.ModelViewSet):
    """
    Реализует следующие операции с моделью Title:
    — получение списка всех произведений;
    - получение информации о конкретном произведении;
    - добавление нового произведения;
    - обновление информации о произведении;
    - удаление произведения.
    """
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    ordering = ('rating', 'title')

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return TitlePostPatchSerializer
        return TitleSerializer


class GenresCategoriesViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый вьюсет для моделей Genre и Category.
    """
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(GenresCategoriesViewSet):
    """
    Реализует операции с моделью Genre:
    — получение списка всех жанров;
    — добавление нового жанра;
    — удаление жанра.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(GenresCategoriesViewSet):
    """
    Реализует операции с моделью Category:
    — получение списка всех категорий;
    — добавление новой категории;
    — удаление категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Реализует операции с моделью Review:
    — получение списка всех отзывов;
    - получение конкретного отзыва;
    — добавление нового отзыва;
    — частичное обновление отзыва;
    — удаление отзыва.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnlyPermission,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    Реализует операции с моделью Comment:
    — получение списка всех комментариев;
    - получение конкретного комментария;
    — добавление нового комментария;
    — частичное обновление комментария;
    — удаление комментария.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnlyPermission,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
