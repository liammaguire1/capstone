from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("menu", views.menu, name="menu"),
    path("game_load", views.game_load, name="game_load"),
    path("game_api/<str:answer>", views.game_api, name="game_api"),
    path("leaderboard", views.leaderboard, name="leaderboard")
]