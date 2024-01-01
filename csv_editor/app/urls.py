from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("test", views.test, name="test"),
    path("upload", views.upload, name="upload"),
    path("create", views.create, name="create"),
    path("export", views.export, name="export"),
    path("delete/<str:id>", views.delete, name="delete"),
    path("edit/<str:id>", views.edit, name="edit"),
    path("update", views.update, name="update"),
    path("clear_all", views.clear_all, name="clear_all"),
    path("search", views.search, name="search"),
    path("sortByHeader/<str:header>", views.sortByHeader, name="sortByHeader"),
]
