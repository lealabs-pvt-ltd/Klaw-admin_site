from rest_framework import serializers

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# from .models import Course
# import os

# class CourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = '__all__'

#     def validate_file_input(self, value):
#         # Check if the file is a PDF or TXT
#         valid_extensions = ['.pdf', '.txt']
#         ext = os.path.splitext(value.name)[1].lower()
#         if ext not in valid_extensions:
#             raise serializers.ValidationError("Only PDF and TXT files are allowed.")
        
#         # Check if the file size is less than or equal to 20MB
#         max_size = 20 * 1024 * 1024  # 20MB
#         if value.size > max_size:
#             raise serializers.ValidationError("File size cannot exceed 20MB.")
        
#         return value

from rest_framework import serializers
from .models import Course
import os
class CourseSerializer(serializers.ModelSerializer):
    file_input = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False  # Optional for updates
    )
    university = serializers.CharField(default="Not Provided", allow_blank=True)
    description = serializers.CharField(default="No description available.", allow_blank=True)
    status = serializers.ChoiceField(choices=Course.STATUS_CHOICES, required=True)  # Make status required

    class Meta:
        model = Course
        fields = '__all__'

    def validate_file_input(self, value):
        valid_extensions = ['.pdf', '.txt']
        max_size = 20 * 1024 * 1024  # 20MB per file

        for file in value:
            # Validate file extension
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    f"File '{file.name}' has an invalid extension. Only PDF and TXT files are allowed."
                )

            # Validate file size
            if file.size > max_size:
                raise serializers.ValidationError(
                    f"File '{file.name}' exceeds the size limit of 20MB."
                )

        return value

    def create(self, validated_data):
        # Extract file input
        files = validated_data.pop('file_input', [])
        file_paths = []
        status = validated_data.get('status', 'draft')  # Ensure status is passed correctly

        # Save the files to disk and collect file paths
        for file in files:
            file_path = f"uploads/{file.name}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            file_paths.append(file_path)

        # Create the Course instance and save metadata along with file paths
        course = Course.objects.create(
            title=validated_data['title'],
            course_code=validated_data['course_code'],
            university=validated_data.get('university', 'Not Provided'),
            description=validated_data.get('description', 'No description available.'),
            file_input=file_paths,
            status=status  # Pass the correct status
        )

        # Assuming vectorization will be handled after saving the files
        course.vectorized_data = {"status": "pending", "details": "Vectorization in progress."}
        course.save()

        return course

    def update(self, instance, validated_data):
        # Update basic fields
        for attr, value in validated_data.items():
            if attr != "file_input":
                setattr(instance, attr, value)

        # Handle file updates (if provided)
        new_files = validated_data.get('file_input', [])
        if new_files:
            file_paths = instance.file_input
            for file in new_files:
                file_path = f"uploads/{file.name}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                file_paths.append(file_path)

            # Save updated file paths
            instance.file_input = file_paths

        instance.save()
        return instance




from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'




# from .models import DummyCourse
# from rest_framework import serializers
# import os

# class DummyCourseSerializer(serializers.ModelSerializer):
#     file_inputs = serializers.ListField(
#         child=serializers.FileField(),
#         allow_empty=False,
#         write_only=True
#     )

#     class Meta:
        
#         model = DummyCourse
#         fields = '__all__'

#     def validate_file_inputs(self, value):
#         valid_extensions = ['.pdf', '.txt']
#         max_size = 20 * 1024 * 1024  # 20MB per file

#         for file in value:
#             # Validate file extension
#             ext = os.path.splitext(file.name)[1].lower()
#             if ext not in valid_extensions:
#                 raise serializers.ValidationError(
#                     f"File '{file.name}' has an invalid extension. Only PDF and TXT files are allowed."
#                 )
            
#             # Validate file size
#             if file.size > max_size:
#                 raise serializers.ValidationError(
#                     f"File '{file.name}' exceeds the size limit of 20MB."
#                 )

#         return value

#     def create(self, validated_data):
#         files = validated_data.pop('file_inputs')
#         file_paths = []
        
#         # Save files to disk
#         for file in files:
#             file_path = f"uploads/{file.name}"
#             with open(file_path, 'wb') as f:
#                 for chunk in file.chunks():
#                     f.write(chunk)
#             file_paths.append(file_path)

#         # Save metadata into the model
#         dummy_course = DummyCourse.objects.create(title=validated_data['title'], file_inputs=file_paths)
#         return dummy_course
