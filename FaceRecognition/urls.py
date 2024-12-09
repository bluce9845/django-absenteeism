from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('FaceDetec.urls')),
    path('admin/', admin.site.urls)
]
