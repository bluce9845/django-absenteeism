# Generated by Django 4.1 on 2024-12-06 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FaceDetec', '0003_attendance_face_encoding_alter_attendance_age_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='attendance_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
