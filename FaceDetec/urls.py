from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='input_data'),
    path("detec/", detec, name="scan_face")
]
