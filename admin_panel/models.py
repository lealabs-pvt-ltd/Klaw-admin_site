from django.db import models
from djongo import models
from bson import ObjectId
#from admin_app.models import Course

class Course(models.Model):
    _id = models.ObjectIdField(primary_key=True)  # MongoDB will handle _id as the primary key
    title = models.CharField(max_length=255)
    course_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    university = models.CharField(max_length=255)
    
    # Store multiple files as a list of file fields in the serializer, but here it's a single FileField
    #file_input = models.ListField(models.CharField(max_length=255), blank=True) 
    file_input = models.JSONField(default=list) 
    vectorized_data = models.JSONField(default=dict)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title

    
# from djongo import models

# class Course(models.Model):
#     # MongoDB will automatically handle _id as the primary key (ObjectId)
#     _id = models.ObjectIdField(primary_key=True)  # Explicitly define _id field if needed
#     title = models.CharField(max_length=255)
#     course_code = models.CharField(max_length=50, unique=True ) 
#     description = models.TextField()
#     university = models.CharField(max_length=255)
#     file_input = models.FileField(upload_to='subject_files/')
#     vectorized_data = models.JSONField(default=dict)
#     STATUS_CHOICES = [
#         ('draft', 'Draft'),
#         ('published', 'Published'),
#     ]
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

#     def __str__(self):
#         return self.title

from djongo import models

class Contact(models.Model):
    # MongoDB will automatically handle _id as the primary key (ObjectId)
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    how_did_you_find_us = models.CharField(max_length=255)

    def __str__(self):
        return f"Contact entry from {self.name}"

# from bson import ObjectId
# from djongo import models

# class DummyCourse(models.Model):
#     _id = models.ObjectIdField(primary_key=True, default=ObjectId) 
#     title = models.CharField(max_length=255)
#     file_inputs = models.JSONField(default=list)  # Store metadata for multiple files
