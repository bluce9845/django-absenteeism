from django.db import models

class Attendance(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    face_path = models.TextField(null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True)  # Menyimpan encoding sebagai JSON
    attendance_date = models.DateTimeField(null=True, blank=True, auto_now=True)
