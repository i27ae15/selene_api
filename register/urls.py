from django.urls import path, re_path
from .views import CreateUserView


urlpatterns = [

    path('create-user/', CreateUserView.as_view(), name='create-user'),
]