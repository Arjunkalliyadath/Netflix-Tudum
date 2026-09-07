from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("form/", views.form_view, name="form"),
    path("register/", views.register, name="register"),
    path("my-list/", views.my_list, name="my_list"),
    # Kept for backwards compatibility with the old /home/ URL.
    path("home/", views.home_page, name="home_page"),
]
