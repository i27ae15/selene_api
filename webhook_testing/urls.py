from django.urls import path
from .views import propertyTest

urlpatterns = [

    path('property-test/', propertyTest.as_view())

]
