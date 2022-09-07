from .views import TrainingAPI
from django.urls import path

urlpatterns = [

   path('training/', TrainingAPI.as_view()),

]
