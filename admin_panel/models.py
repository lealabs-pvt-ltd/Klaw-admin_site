from django.db import models
from djongo import models
from bson import ObjectId
import datetime

class CourseBasicInfo(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=50, unique=True)
    year = models.IntegerField()
    branch = models.CharField(max_length=100)
    semester = models.IntegerField()
    group = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"

class CourseOutcome(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    course_code = models.CharField(max_length=50, db_index=True)
    short_form = models.CharField(max_length=10)
    outcome = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code}: {self.short_form}"

class CourseSyllabus(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    course_code = models.CharField(max_length=50, db_index=True)
    syllabus_item = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code}: {self.syllabus_item[:50]}"

class CourseQuestion(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    course_code = models.CharField(max_length=50, db_index=True)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code}: {self.question[:50]}"

class CourseMaterial(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    course_code = models.CharField(max_length=50, db_index=True)
    file_path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code}: {self.file_type} ({self.file_path})"

class Course(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    course_code = models.CharField(max_length=50, unique=True)
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Course {self.course_code} ({self.status})"

class Contact(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    how_did_you_find_us = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Contact entry from {self.name}"

class Blog(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('publish', 'Published'),
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    html_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"{self.title} - {self.status}"


 #Notification model
class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']



class AdminAppUser(models.Model):
    class Meta:
        managed = False  # Prevent Django from trying to create/migrate this model
        db_table = 'mobile_api_appuser'  # Ensure this matches your MongoDB collection name
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    id = models.IntegerField(primary_key=True)  # This is the MongoDB _id field
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)  # Add email field
    year_of_study = models.CharField(
        max_length=10,
        choices=[
            ('1st year', '1st year'),
            ('2nd year', '2nd year'),
            ('3rd year', '3rd year'),
            ('4th year', '4th year')
        ],
        null=True,
        blank=True
    )
    college = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    university = models.CharField(max_length=100, null=True, blank=True)
    blood_group = models.CharField(max_length=3, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    subscription_plan = models.CharField(
        max_length=50,
        choices=[('Plan 1', 'Plan 1'), ('Plan 2', 'Plan 2'), ('Plan 3', 'Plan 3')],
        default='Plan 1'
    )
    status = models.CharField(max_length=20, choices=[('accepted', 'Accepted'), ('rejected', 'Rejected')], default='rejected')

    def __str__(self):
        return self.full_name if self.full_name else self.phone_number
