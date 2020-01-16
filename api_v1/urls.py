from django.urls import path, include


urlpatterns = [
    path('', include('api_v1.urls'))
]
