from django.urls import include, path


urlpatterns = [
    path('v1/', include('cinema.api.v1.urls')),
]