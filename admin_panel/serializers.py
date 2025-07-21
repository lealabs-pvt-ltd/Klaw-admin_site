from rest_framework import serializers
from .models import CourseBasicInfo, CourseOutcome, CourseSyllabus, CourseQuestion, CourseMaterial, Course, Contact, Blog, Notification
import os
from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class CourseBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseBasicInfo
        fields = ['course_name', 'course_code', 'year', 'branch', 'semester', 'group']

    def validate_course_code(self, value):
        if CourseBasicInfo.objects.filter(course_code=value).exists():
            raise serializers.ValidationError("Course code already exists.")
        return value

class CourseOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOutcome
        fields = ['course_code', 'short_form', 'outcome']

    def validate(self, data):
        if not data.get('course_code'):
            raise serializers.ValidationError({"course_code": "This field is required."})
        if not data.get('short_form') or not data['short_form'].strip():
            raise serializers.ValidationError({"short_form": "This field is required and cannot be empty."})
        if not data.get('outcome') or not data['outcome'].strip():
            raise serializers.ValidationError({"outcome": "This field is required and cannot be empty."})
        if not CourseBasicInfo.objects.filter(course_code=data['course_code']).exists():
            raise serializers.ValidationError({"course_code": "Course code does not exist."})
        return data

class CourseSyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSyllabus
        fields = ['course_code', 'syllabus_item']

    def validate_course_code(self, value):
        if not CourseBasicInfo.objects.filter(course_code=value).exists():
            raise serializers.ValidationError("Course code does not exist.")
        return value

class CourseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseQuestion
        fields = ['course_code', 'question']

    def validate_course_code(self, value):
        if not CourseBasicInfo.objects.filter(course_code=value).exists():
            raise serializers.ValidationError("Course code does not exist.")
        return value

class CourseMaterialSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_type = serializers.CharField()
    file_path = serializers.CharField(read_only=True)

    class Meta:
        model = CourseMaterial
        fields = ['course_code', 'file', 'file_type', 'file_path']

    def validate_file(self, value):
        valid_extensions = ['.pdf', '.txt']
        max_size = 100 * 1024 * 1024  # 100MB
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"File '{value.name}' has invalid extension. Only PDF and TXT allowed.")
        if value.size > max_size:
            raise serializers.ValidationError(f"File '{value.name}' exceeds 100MB limit.")
        return value

    def validate_course_code(self, value):
        if not CourseBasicInfo.objects.filter(course_code=value).exists():
            raise serializers.ValidationError("Course code does not exist.")
        return value

    def create(self, validated_data):
        file = validated_data.pop('file')
        file_type = validated_data.pop('file_type')
        fs = FileSystemStorage(location='media/')
        filename = fs.save(file.name, file)
        file_path = fs.url(filename)  # Store relative path
        return CourseMaterial.objects.create(
            course_code=validated_data['course_code'],
            file_path=file_path,
            file_type=file_type
        )

class CourseDetailSerializer(serializers.ModelSerializer):
    basic_info = serializers.SerializerMethodField()
    outcomes = serializers.SerializerMethodField()
    syllabus = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['course_code', 'status', 'basic_info', 'outcomes', 'syllabus', 'questions', 'materials', 'created_at', 'updated_at']

    def get_basic_info(self, obj):
        try:
            basic_info = CourseBasicInfo.objects.get(course_code=obj.course_code)
            return CourseBasicInfoSerializer(basic_info).data
        except CourseBasicInfo.DoesNotExist:
            return None

    def get_outcomes(self, obj):
        outcomes = CourseOutcome.objects.filter(course_code=obj.course_code)
        return CourseOutcomeSerializer(outcomes, many=True).data

    def get_syllabus(self, obj):
        syllabus = CourseSyllabus.objects.filter(course_code=obj.course_code)
        return CourseSyllabusSerializer(syllabus, many=True).data

    def get_questions(self, obj):
        questions = CourseQuestion.objects.filter(course_code=obj.course_code)
        return CourseQuestionSerializer(questions, many=True).data

    def get_materials(self, obj):
        materials = CourseMaterial.objects.filter(course_code=obj.course_code)
        return [{'file_path': m.file_path, 'file_type': m.file_type} for m in materials]

class CourseFinalSerializer(serializers.ModelSerializer):
    materials = CourseMaterialSerializer(many=True)
    status = serializers.ChoiceField(choices=Course.STATUS_CHOICES, default='draft')

    class Meta:
        model = Course
        fields = ['course_code', 'status', 'materials']

    def validate(self, data):
        if not data.get('course_code'):
            raise serializers.ValidationError({"course_code": "This field is required."})
        if not data.get('materials'):
            raise serializers.ValidationError({"materials": "At least one material is required."})
        if not CourseBasicInfo.objects.filter(course_code=data['course_code']).exists():
            raise serializers.ValidationError({"course_code": "Course code does not exist."})
        if Course.objects.filter(course_code=data['course_code']).exists():
            raise serializers.ValidationError({"course_code": "Course already finalized."})
        return data

    def create(self, validated_data):
        materials_data = validated_data.pop('materials')
        course = Course.objects.create(**validated_data)
        
        fs = FileSystemStorage(location='media/')
        for material_data in materials_data:
            file = material_data.pop('file')
            file_type = material_data.pop('file_type')
            filename = fs.save(file.name, file)
            file_path = fs.url(filename)  # Store relative path
            CourseMaterial.objects.create(
                course_code=validated_data['course_code'],
                file_path=file_path,
                file_type=file_type
            )
        
        return course

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(choices=Blog.STATUS_CHOICES, default='draft')

    class Meta:
        model = Blog
        fields = ['id', 'title', 'author', 'category', 'html_code', 'created_at', 'status']

    def validate(self, data):
        if not data.get('title'):
            raise serializers.ValidationError({"title": "This field is required."})
        if not data.get('author'):
            raise serializers.ValidationError({"author": "This field is required."})
        if not data.get('category'):
            raise serializers.ValidationError({"category": "This field is required."})
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at']

    def validate(self, data):
        if not data.get('title') or not data['title'].strip():
            raise serializers.ValidationError({"title": "Title is required and cannot be empty."})
        if not data.get('message') or not data['message'].strip():
            raise serializers.ValidationError({"message": "Message is required and cannot be empty."})
        return data