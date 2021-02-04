from django.urls import path

from cinema.api.v1 import views

urlpatterns = [
    path('movies/', views.MoviesListApi.as_view()),
    path('test/', views.Movies.as_view()),
]