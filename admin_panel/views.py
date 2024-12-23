from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.files.storage import FileSystemStorage
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from .serializers import AdminLoginSerializer
from rest_framework import status  
from .models import Course
from .serializers import CourseSerializer
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from vectorization.add import add
import os
import logging
import json
import traceback
from django.core.files.storage import FileSystemStorage
# from .models import RevokedToken 

class AdminLoginView(APIView):
    permission_classes = []  # No permissions needed if using superuser login for simplicity

    def post(self, request):
        """
        Authenticate the superuser and return JWT tokens (access & refresh).
        """
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:  # Check if it's the superuser
                try:
                    # Generate JWT tokens (access & refresh)
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'detail': f'Error generating token: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'detail': 'Invalid credentials or not an admin user.'},
                                status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def vectorize_file(file_path):
    # Simulate vectorization (replace with actual logic)
    if file_path:  # Check if the file exists and is valid
        return {"vector": f"Vectorized data from {file_path}"}
    return {}  # Return an empty dictionary if vectorization fails


# class AddCourseView(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is logged in

#     def post(self, request):
#         # Step 1: Validate if the course_code already exists
#         course_code = request.data.get("course_code")
#         existing_course = Course.objects.filter(course_code=course_code).first()
        
#         if existing_course:
#             return Response({"error": "Course with this course code already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Step 2: Deserialize the incoming data
#         serializer = CourseSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save the course first
#             course = serializer.save()

#             # Step 3: Check if file_input exists and process vectorized data
#             file_path = course.file_input.path if course.file_input else None

#             # If file exists, vectorize and store the result
#             if file_path:
#                 dbname = f"course_{course.course_code}"  # Use course _id as the database name for vectorization
#                 try:
#                     # Perform vectorization by calling the add function
#                     vectorization_status = add(dbname, file_path)
                    
#                     if vectorization_status:
#                         # Ensure vectorized_data is a dictionary, not a string
#                         course.vectorized_data = {"status": "success", "details": vectorization_status}
#                     else:
#                         course.vectorized_data = {"status": "failed", "details": "Vectorization failed."}
#                 except Exception as e:
#                     course.vectorized_data = {"status": "error", "details": str(e)}
            
#             # Step 4: Save the updated course object with the vectorized data
#             course.save()

#             # Return the serialized data with vectorized_data correctly populated
#             return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AddCourseView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def post(self, request):
        # Debugging - print the request data
        print("REQUEST DATA:", request.data)

        # Step 1: Validate if the course_code already exists
        course_code = request.data.get("course_code")
        existing_course = Course.objects.filter(course_code=course_code).first()

        if existing_course:
            return Response({"error": "Course with this course code already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Deserialize the incoming data
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            # Save the course and handle files
            course = serializer.save()

            # File handling and vectorization
            files = request.FILES.getlist('file_input')
            print("FILES RECEIVED:", files)  # Debugging

            file_paths = []
            vectorization_statuses = []

            for file in files:
                # Save the file to disk
                try:
                    fs = FileSystemStorage(location='media/')
                    filename = fs.save(file.name, file)
                    file_path = fs.path(filename)
                    file_paths.append(file_path)

                    # Vectorization
                    dbname = f"course_{course.course_code}"
                    vectorization_status = add(dbname, file_path)
                    vectorization_statuses.append({"file": file.name, "status": "success", "details": vectorization_status})
                except Exception as e:
                    vectorization_statuses.append({"file": file.name, "status": "failed", "details": str(e)})
                    print("ERROR SAVING FILE OR VECTORIZE:", str(e))  # Debugging

            # Update vectorized data and save paths
            course.vectorized_data = {"status": "completed", "details": vectorization_statuses}
            course.file_input = file_paths
            course.save()

            # Debugging - print the status after saving the course
            print("COURSE STATUS AFTER SAVE:", course.status)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Debug serializer errors
        print("VALIDATION ERRORS:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from bson import ObjectId
class ToggleCourseStatusView(APIView):
    permission_classes = [IsAuthenticated]  # Require login

    def post(self, request, pk):
        try:
            # Convert pk to ObjectId explicitly
            course = Course.objects.get(_id=ObjectId(pk))
            
            # Delete the course if requested
            if 'delete' in request.data and request.data['delete']:
                course.delete()
                return Response({'detail': 'Course deleted successfully.'}, status=status.HTTP_200_OK)

            # Toggle between "Draft" and "Published"
            course.status = 'published' if course.status == 'draft' else 'draft'
            course.save()
            return Response({'status': course.status}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

# class ToggleCourseStatusView(APIView):
#     def get(self, request, pk):
#         try:
#             course = Course.objects.get(_id=pk)
#             return Response({"course": str(course)}, status=status.HTTP_200_OK)
#         except Course.DoesNotExist:
#             return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

class GetCoursesView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def get(self, request):
        # Get the 'status' parameter from the query string
        status_filter = request.query_params.get('status')
        if status_filter not in ['draft', 'published']:
            return Response({"error": "Invalid status filter. Use 'draft' or 'published'."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter courses based on status
        courses = Course.objects.filter(status=status_filter)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from .models import Contact
from .serializers import ContactSerializer

class ContactFormView(APIView):
    permission_classes = []  # Override global authentication settings
    authentication_classes = []  # Optional: explicitly disable authentication

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contact entry successfully submitted!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# from .models import DummyCourse
# from .serializers import DummyCourseSerializer

# class DummyCourseView(APIView):
#     permission_classes = []  # Override global authentication settings
#     authentication_classes = [] 
#     def post(self, request):
#         # Step 1: Validate the input data
#         serializer = DummyCourseSerializer(data=request.data)
#         if serializer.is_valid():
#             # Step 2: Save the course
#             course = serializer.save()

#             # Step 3: Simulate vectorization for each file
#             file_metadata = []
#             for file in request.FILES.getlist('file_inputs'):
#                 try:
#                     # Simulate vectorization - Replace this with your actual function call
#                     vector_data = add(dbname, file_path)
#                     file_metadata.append({
#                         "file_name": file.name,
#                         "vectorized": True,
#                         "details": vector_data
#                     })
#                 except Exception as e:
#                     file_metadata.append({
#                         "file_name": file.name,
#                         "vectorized": False,
#                         "error": str(e)
#                     })

#             # Update the course with file metadata
#             course.file_inputs = file_metadata
#             course.save()

#             # Return the response with the vectorized data
#             return Response({
#                 "message": "Files processed successfully.",
#                 "data": DummyCourseSerializer(course).data
#             }, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def vectorize_file(self, file):
#         # Dummy vectorization function
#         # Replace this with your actual vectorization logic
#         return f"Vector data for {file.name}"



# Edit course details - restricted to draft courses

class EditCourseView(APIView):
    permission_classes = [IsAuthenticated]  # Require login

    def patch(self, request, pk):
        try:
            # Fetch the course object by ID
            course = Course.objects.get(_id=ObjectId(pk))

            # Allow editing only if the course is in "Draft" status
            if course.status != 'draft':
                return Response({"error": "Editing is only allowed for draft courses."}, status=status.HTTP_403_FORBIDDEN)

            # Handle partial updates for course details
            data = request.data
            serializer = CourseSerializer(course, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Handle file uploads and vectorization
                new_files = request.FILES.getlist('file_input')
                new_file_paths = []
                vectorization_statuses = course.vectorized_data.get("details", [])

                for file in new_files:
                    # Save the new file
                    fs = FileSystemStorage(location='media/')
                    filename = fs.save(file.name, file)
                    file_path = fs.path(filename)
                    new_file_paths.append(file_path)

                    # Perform vectorization only on the new files
                    dbname = f"course_{course.course_code}"
                    try:
                        vectorization_status = add(dbname, file_path)  # Assuming 'add' handles the vectorization
                        vectorization_statuses.append({"file": file.name, "status": "success", "details": vectorization_status})
                    except Exception as e:
                        vectorization_statuses.append({"file": file.name, "status": "failed", "details": str(e)})

                # Update file paths and vectorization status
                course.file_input.extend(new_file_paths)
                course.vectorized_data = {"status": "completed", "details": vectorization_statuses}

                # Save course object
                course.save()

                return Response({"detail": "Course updated successfully.", "course": CourseSerializer(course).data}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
