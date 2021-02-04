from django.urls import path

from cinema.api.v1 import views

urlpatterns = [
    path('test/', views.MoviesListApi.as_view()),
    path('movies/', views.Movies.as_view()),
]