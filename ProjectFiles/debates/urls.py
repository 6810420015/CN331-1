from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.topic_list, name="topic_list"),
    path("topic/<int:topic_id>/", views.topic_detail, name="topic_detail"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="debates/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("create/", views.create_topic, name="create_topic"),
    path("topic/<int:topic_id>/delete/", views.delete_topic, name="delete_topic"),
    path("topic/<int:topic_id>/edit/", views.edit_topic, name="edit_topic"),
    path("profile/", views.user_profile, name="user_profile"),
]
