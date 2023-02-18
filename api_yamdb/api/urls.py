from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriesViewSet,
    CommentViewSet,
    GenresViewSet,
    ReviewViewSet,
    TitlesViewSet,
    UserViewSet,
    SignUpView,
    GetTokenView
)

router_v1 = DefaultRouter()
router_v1.register(
    r'users',
    UserViewSet,
    basename='users'
)
router_v1.register(
    r'titles',
    TitlesViewSet,
    basename='titles'
)
router_v1.register(
    r'categories',
    CategoriesViewSet,
    basename='categories'
)
router_v1.register(
    r'genres',
    GenresViewSet,
    basename='genres'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router_v1.register(
    r'titles/(?P<titles_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

registration_uls = [
    path('signup/', SignUpView.as_view()),
    path('token/', GetTokenView.as_view()),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(registration_uls)),
]
