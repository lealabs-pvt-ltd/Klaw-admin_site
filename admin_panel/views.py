from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views import View 
from .models import AdminAppUser
import urllib.parse
from .models import CourseBasicInfo, CourseOutcome, CourseSyllabus, CourseQuestion, CourseMaterial, Course, Contact, Blog, Notification
from .serializers import (
    AdminLoginSerializer, CourseBasicInfoSerializer, CourseOutcomeSerializer,
    CourseSyllabusSerializer, CourseQuestionSerializer, CourseMaterialSerializer,
    CourseFinalSerializer, ContactSerializer, BlogSerializer, CourseDetailSerializer, 
    NotificationSerializer
)
from django.core.files.storage import FileSystemStorage
import logging
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bson import ObjectId
from .utils import send_notification_to_topic
logger = logging.getLogger(__name__)
load_dotenv()


class AdminLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                try:
                    refresh = RefreshToken.for_user(user)
                    logger.info(f"Admin login successful: {username}")
                    return Response({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Error generating token for {username}: {str(e)}")
                    return Response({'detail': f'Error generating token: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logger.warning(f"Invalid login attempt: {username}")
                return Response({'detail': 'Invalid credentials or not an admin user.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseBasicInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CourseBasicInfoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            logger.info(f"Course basic info created: {instance.course_code}")
            return Response({"course_code": instance.course_code, "message": "successful"}, status=status.HTTP_201_CREATED)
        logger.error(f"Course basic info creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            if course.status != 'draft':
                logger.error(f"Edit attempt on non-draft course: {course_code}")
                return Response({"error": "Only draft courses can be edited."}, status=status.HTTP_403_FORBIDDEN)
            
            try:
                basic_info = CourseBasicInfo.objects.get(course_code=course_code)
            except CourseBasicInfo.DoesNotExist:
                logger.error(f"Course basic info not found: {course_code}")
                return Response({"error": "Course basic info not found."}, status=status.HTTP_404_NOT_FOUND)

            # Prevent course_code update
            if 'course_code' in request.data:
                logger.error(f"Attempt to modify course_code: {course_code}")
                return Response({"error": "Course code cannot be modified."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = CourseBasicInfoSerializer(basic_info, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                logger.info(f"Course basic info updated: {course_code}")
                return Response({"message": "successful", "course_code": course_code}, status=status.HTTP_200_OK)
            logger.error(f"Course basic info update failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class CourseOutcomesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_code = request.data.get('course_code')
        outcomes = request.data.get('outcomes', [])
        if not course_code:
            logger.error("Course outcomes creation failed: No course code provided")
            return Response({"error": "Course code is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not outcomes:
            logger.error("Course outcomes creation failed: No outcomes provided")
            return Response({"error": "At least one outcome is required."}, status=status.HTTP_400_BAD_REQUEST)
        for outcome_data in outcomes:
            if not outcome_data.get('short_form', '').strip() or not outcome_data.get('outcome', '').strip():
                logger.error("Course outcomes creation failed: Empty short_form or outcome")
                return Response({"error": "Each outcome must have a non-empty short_form and outcome."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CourseOutcomeSerializer(data={**outcome_data, 'course_code': course_code})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Course outcome added: {course_code} - {outcome_data.get('short_form')}")
            else:
                logger.error(f"Course outcome creation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"course_code": course_code, "message": "successful"}, status=status.HTTP_201_CREATED)

    def patch(self, request, course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            if course.status != 'draft':
                logger.error(f"Edit attempt on non-draft course: {course_code}")
                return Response({"error": "Only draft courses can be edited."}, status=status.HTTP_403_FORBIDDEN)

            outcomes_data = request.data.get('outcomes', [])
            if not outcomes_data:
                logger.error("Course outcomes update failed: No outcomes provided")
                return Response({"error": "At least one outcome is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate uniqueness of short_form in the request
            short_forms = [outcome.get('short_form', '').strip() for outcome in outcomes_data]
            if len(short_forms) != len(set(short_forms)):
                logger.error(f"Course outcomes update failed: Duplicate short_form values in {course_code}")
                return Response({"error": "Outcome short_form values must be unique."}, status=status.HTTP_400_BAD_REQUEST)

            # Delete existing outcomes
            deleted_count = CourseOutcome.objects.filter(course_code=course_code).delete()[0]
            logger.info(f"Deleted {deleted_count} existing outcomes for course: {course_code}")

            # Create new outcomes
            created_outcomes = []
            for outcome_data in outcomes_data:
                if 'course_code' in outcome_data:
                    logger.error(f"Attempt to modify course_code in outcome: {course_code}")
                    return Response({"error": "Course code cannot be modified in outcomes."}, status=status.HTTP_400_BAD_REQUEST)
                if not outcome_data.get('short_form', '').strip() or not outcome_data.get('outcome', '').strip():
                    logger.error(f"Course outcomes update failed: Empty short_form or outcome for {course_code}")
                    return Response({"error": "Each outcome must have a non-empty short_form and outcome."}, status=status.HTTP_400_BAD_REQUEST)
                serializer = CourseOutcomeSerializer(data={**outcome_data, 'course_code': course_code})
                if serializer.is_valid():
                    serializer.save()
                    created_outcomes.append(outcome_data.get('short_form'))
                else:
                    logger.error(f"Course outcome update failed: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Course outcomes updated: {course_code} - {len(created_outcomes)} outcomes added: {created_outcomes}")
            return Response({"message": "successful", "course_code": course_code}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class CourseSyllabusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_code = request.data.get('course_code')
        syllabus_items = request.data.get('syllabus_items', [])
        if not course_code:
            logger.error("Course syllabus creation failed: No course code provided")
            return Response({"error": "Course code is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not syllabus_items:
            logger.error("Course syllabus creation failed: No syllabus items provided")
            return Response({"error": "At least one syllabus item is required."}, status=status.HTTP_400_BAD_REQUEST)
        for item in syllabus_items:
            if not item.strip():
                logger.error("Course syllabus creation failed: Empty syllabus item")
                return Response({"error": "Each syllabus item must be non-empty."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CourseSyllabusSerializer(data={'course_code': course_code, 'syllabus_item': item})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Syllabus item added: {course_code}")
            else:
                logger.error(f"Syllabus item creation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"course_code": course_code, "message": "successful"}, status=status.HTTP_201_CREATED)

    def patch(self, request, course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            if course.status != 'draft':
                logger.error(f"Edit attempt on non-draft course: {course_code}")
                return Response({"error": "Only draft courses can be edited."}, status=status.HTTP_403_FORBIDDEN)

            syllabus_items = request.data.get('syllabus_items', [])
            if not syllabus_items:
                logger.error("Course syllabus update failed: No syllabus items provided")
                return Response({"error": "At least one syllabus item is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate uniqueness of syllabus items in the request
            syllabus_items = [item.strip() for item in syllabus_items if item.strip()]
            if len(syllabus_items) != len(set(syllabus_items)):
                logger.error(f"Course syllabus update failed: Duplicate syllabus items in {course_code}")
                return Response({"error": "Syllabus items must be unique."}, status=status.HTTP_400_BAD_REQUEST)

            # Delete existing syllabus items
            deleted_count = CourseSyllabus.objects.filter(course_code=course_code).delete()[0]
            logger.info(f"Deleted {deleted_count} existing syllabus items for course: {course_code}")

            # Create new syllabus items
            created_items = []
            for item in syllabus_items:
                if not item.strip():
                    logger.error(f"Course syllabus update failed: Empty syllabus item for {course_code}")
                    return Response({"error": "Each syllabus item must be non-empty."}, status=status.HTTP_400_BAD_REQUEST)
                serializer = CourseSyllabusSerializer(data={'course_code': course_code, 'syllabus_item': item})
                if serializer.is_valid():
                    serializer.save()
                    created_items.append(item)
                else:
                    logger.error(f"Syllabus item update failed: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Course syllabus updated: {course_code} - {len(created_items)} items added")
            return Response({"message": "successful", "course_code": course_code}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class CourseQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_code = request.data.get('course_code')
        questions = request.data.get('questions', [])
        if not course_code:
            logger.error("Course questions creation failed: No course code provided")
            return Response({"error": "Course code is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not questions:
            logger.error("Course questions creation failed: No questions provided")
            return Response({"error": "At least one question is required."}, status=status.HTTP_400_BAD_REQUEST)
        for question in questions:
            if not question.strip():
                logger.error("Course questions creation failed: Empty question")
                return Response({"error": "Each question must be non-empty."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CourseQuestionSerializer(data={'course_code': course_code, 'question': question})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Question added: {course_code}")
            else:
                logger.error(f"Question creation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"course_code": course_code, "message": "successful"}, status=status.HTTP_201_CREATED)

    def patch(self, request, course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            if course.status != 'draft':
                logger.error(f"Edit attempt on non-draft course: {course_code}")
                return Response({"error": "Only draft courses can be edited."}, status=status.HTTP_403_FORBIDDEN)

            questions = request.data.get('questions', [])
            if not questions:
                logger.error("Course questions update failed: No questions provided")
                return Response({"error": "At least one question is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate uniqueness of questions in the request
            questions = [question.strip() for question in questions if question.strip()]
            if len(questions) != len(set(questions)):
                logger.error(f"Course questions update failed: Duplicate questions in {course_code}")
                return Response({"error": "Questions must be unique."}, status=status.HTTP_400_BAD_REQUEST)

            # Delete existing questions
            deleted_count = CourseQuestion.objects.filter(course_code=course_code).delete()[0]
            logger.info(f"Deleted {deleted_count} existing questions for course: {course_code}")

            # Create new questions
            created_questions = []
            for question in questions:
                if not question.strip():
                    logger.error(f"Course questions update failed: Empty question for {course_code}")
                    return Response({"error": "Each question must be non-empty."}, status=status.HTTP_400_BAD_REQUEST)
                serializer = CourseQuestionSerializer(data={'course_code': course_code, 'question': question})
                if serializer.is_valid():
                    serializer.save()
                    created_questions.append(question)
                else:
                    logger.error(f"Question update failed: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Course questions updated: {course_code} - {len(created_questions)} questions added")
            return Response({"message": "successful", "course_code": course_code}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class CourseMaterialsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_code = request.data.get('course_code')
        files = request.FILES.getlist('files')
        if not course_code:
            logger.error("Course materials creation failed: No course code provided")
            return Response({"error": "Course code is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not files:
            logger.error("Course materials creation failed: No files provided")
            return Response({"error": "At least one file is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        materials_data = []
        for i, file in enumerate(files):
            file_type = request.data.get(f'file_type_{i}', 'Unknown')
            materials_data.append({
                'course_code': course_code,
                'file': file,
                'file_type': file_type
            })

        serializer = CourseFinalSerializer(data={
            'course_code': course_code,
            'status': request.data.get('status', 'draft'),
            'materials': materials_data
        })
        if serializer.is_valid():
            instance = serializer.save()
            logger.info(f"Course finalized: {instance.course_code} with status {instance.status}")
            return Response({"course_code": instance.course_code, "message": "successful"}, status=status.HTTP_201_CREATED)
        logger.error(f"Course materials creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            if course.status != 'draft':
                logger.error(f"Edit attempt on non-draft course: {course_code}")
                return Response({"error": "Only draft courses can be edited."}, status=status.HTTP_403_FORBIDDEN)

            files = request.FILES.getlist('files')
            if not files:
                logger.error("Course materials update failed: No files provided")
                return Response({"error": "At least one file is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate uniqueness of file names in the request
            file_names = [file.name for file in files]
            if len(file_names) != len(set(file_names)):
                logger.error(f"Course materials update failed: Duplicate file names in {course_code}")
                return Response({"error": "File names must be unique."}, status=status.HTTP_400_BAD_REQUEST)

            # Delete existing materials
            deleted_count = CourseMaterial.objects.filter(course_code=course_code).delete()[0]
            logger.info(f"Deleted {deleted_count} existing materials for course: {course_code}")

            # Create new materials
            created_files = []
            for i, file in enumerate(files):
                file_type = request.data.get(f'file_type_{i}', 'Unknown')
                serializer = CourseMaterialSerializer(data={
                    'course_code': course_code,
                    'file': file,
                    'file_type': file_type
                })
                if serializer.is_valid():
                    serializer.save()
                    created_files.append(file.name)
                else:
                    logger.error(f"Course material update failed: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Course materials updated: {course_code} - {len(created_files)} files added: {created_files}")
            return Response({"message": "successful"}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class CourseDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        course_code = request.query_params.get('course_code')
        if not course_code:
            logger.error("Course deletion failed: No course code provided")
            return Response({"error": "Course code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CourseBasicInfo.objects.filter(course_code=course_code).delete()
            CourseOutcome.objects.filter(course_code=course_code).delete()
            CourseSyllabus.objects.filter(course_code=course_code).delete()
            CourseQuestion.objects.filter(course_code=course_code).delete()
            CourseMaterial.objects.filter(course_code=course_code).delete()
            Course.objects.filter(course_code=course_code).delete()
            
            logger.info(f"Course deleted: {course_code}")
            return Response({"detail": f"Course {course_code} and related data deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting course {course_code}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            serializer = CourseDetailSerializer(course)
            logger.info(f"Retrieved course details for: {course_code}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

class ToggleCourseStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_code):
        if not request.user.is_superuser:
            logger.warning(f"Non-admin attempted to toggle course status: {request.user.username} for course: {course_code}")
            return Response({"error": "Only admin users can toggle course status."}, status=status.HTTP_403_FORBIDDEN)

        try:
            course = Course.objects.get(course_code=course_code)
            course.status = 'published' if course.status == 'draft' else 'draft'
            course.save()
            logger.info(f"Course status toggled: {course.course_code} to {course.status} by user: {request.user.username}")
            return Response({
                "course_code": course.course_code,
                "status": course.status,
                "message": "successful"
            }, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
            
class GetCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get('status')
        if status_filter not in ['draft', 'published']:
            logger.error(f"Invalid status filter: {status_filter}")
            return Response({"error": "Invalid status filter. Use 'draft' or 'published'."}, status=status.HTTP_400_BAD_REQUEST)

        courses = Course.objects.filter(status=status_filter)
        serializer = CourseDetailSerializer(courses, many=True)
        logger.info(f"Retrieved {len(courses)} courses with status {status_filter}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class ContactFormView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            logger.info(f"Contact form submitted: {instance.name}")
            return Response({"message": "Contact entry successfully submitted!"}, status=status.HTTP_201_CREATED)
        logger.error(f"Contact form submission failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            logger.info(f"Blog created: {instance.title} by {instance.author}")
            return Response({"message": "successful"}, status=status.HTTP_201_CREATED)
        logger.error(f"Blog creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListBlogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blogs = Blog.objects.all().order_by('-created_at')
        serializer = BlogSerializer(blogs, many=True)
        logger.info(f"Retrieved {len(blogs)} blogs")
        return Response(serializer.data, status=status.HTTP_200_OK)

class SingleBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
            serializer = BlogSerializer(blog)
            logger.info(f"Retrieved blog: {blog.title} (ID: {id})")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            logger.error(f"Blog not found: ID {id}")
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

class EditBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
            if blog.status != 'draft':
                logger.error(f"Edit attempt on non-draft blog: {blog.title} (ID: {id})")
                return Response({"error": "Editing is only allowed for draft blogs."}, status=status.HTTP_403_FORBIDDEN)
            serializer = BlogSerializer(blog, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                logger.info(f"Blog updated: {instance.title} (ID: {id})")
                return Response({"detail": "Blog updated successfully."}, status=status.HTTP_200_OK)
            logger.error(f"Blog edit failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Blog.DoesNotExist:
            logger.error(f"Blog not found: ID {id}")
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

class ToggleBlogStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
            blog.status = 'publish' if blog.status == 'draft' else 'draft'
            blog.save()
            logger.info(f"Blog status toggled: {blog.title} (ID: {id}) to {blog.status}")
            return Response({"id": blog.id, "message": "successful"}, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            logger.error(f"Blog not found: ID {id}")
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

class DeleteBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
            blog.delete()
            logger.info(f"Blog deleted: {blog.title} (ID: {id})")
            return Response({"message": "successful"}, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            logger.error(f"Blog not found: ID {id}")
            return Response({"detail": "Blog not found."}, status=status.HTTP_404_NOT_FOUND)

# New Notification Views
class PushNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            logger.warning(f"Non-admin attempted to send notification: {request.user.username}")
            return Response({"error": "Only admin users can send notifications."}, status=status.HTTP_403_FORBIDDEN)

        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            fcm_response = send_notification_to_topic(
                title=notification.title,
                message=notification.message
            )
            logger.info(f"Notification saved and sent: {notification.title} (ID: {notification.id})")
            return Response({
                "message": "Notification sent successfully",
                "notification": serializer.data,
                "fcm_response": fcm_response
            }, status=status.HTTP_201_CREATED)
        logger.error(f"Notification creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        logger.info(f"Retrieved {len(notifications)} notifications for user: {request.user.username}")
        return Response(serializer.data, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)
load_dotenv()

class ProcessCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            logger.warning(f"Non-admin attempted to process course: {request.user.username}")
            return Response({"error": "Only admin users can process courses."}, status=status.HTTP_403_FORBIDDEN)

        course_code = request.data.get("course_code")
        if not course_code:
            logger.error("Process course failed: No course code provided")
            return Response({"error": "Course code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(course_code=course_code)
            if course.status != "draft":
                logger.error(f"Process course failed: Course {course_code} is not in draft status")
                return Response({"error": "Only draft courses can be processed."}, status=status.HTTP_403_FORBIDDEN)

            # Initialize response structure
            results = {
                "basic_info": "success",
                "course_outcome": "success",
                "syllabus": "success",
                "questions": "success",
                "materials": "success",
                "trigger": "success"
            }
            ai_server_url = os.getenv("AI_SERVER", "http://127.0.0.1:5000")

            # 1. Basic Info
            try:
                basic_info = CourseBasicInfo.objects.get(course_code=course_code)
                basic_info_data = {
                    "course_name": basic_info.course_name,
                    "course_code": basic_info.course_code,
                    "year": basic_info.year,
                    "branch": basic_info.branch,
                    "semester": basic_info.semester,
                    "group": basic_info.group
                }
                response = requests.post(f"{ai_server_url}/api/basic_info", json=basic_info_data)
                response.raise_for_status()
                logger.info(f"Basic info sent for course: {course_code}")
            except CourseBasicInfo.DoesNotExist:
                logger.error(f"Basic info not found for course: {course_code}")
                results["basic_info"] = "error: Basic info not found"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_400_BAD_REQUEST)
            except requests.RequestException as e:
                logger.error(f"Failed to send basic info for course {course_code}: {str(e)}")
                results["basic_info"] = f"error: {str(e)}"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 2. Course Outcomes
            try:
                outcomes = CourseOutcome.objects.filter(course_code=course_code)
                if not outcomes:
                    logger.error(f"No outcomes found for course: {course_code}")
                    results["course_outcome"] = "error: No outcomes found"
                    return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_400_BAD_REQUEST)
                for outcome in outcomes:
                    outcome_data = {
                        "course_code": outcome.course_code,
                        "shortform_course_code": outcome.short_form,
                        "course_outcome": outcome.outcome
                    }
                    response = requests.post(f"{ai_server_url}/api/course_outcome", json=outcome_data)
                    response.raise_for_status()
                logger.info(f"Outcomes sent for course: {course_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to send outcomes for course {course_code}: {str(e)}")
                results["course_outcome"] = f"error: {str(e)}"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 3. Syllabus
            try:
                syllabus_items = CourseSyllabus.objects.filter(course_code=course_code)
                if not syllabus_items:
                    logger.error(f"No syllabus items found for course: {course_code}")
                    results["syllabus"] = "error: No syllabus items found"
                    return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_400_BAD_REQUEST)
                for item in syllabus_items:
                    syllabus_data = {
                        "course_code": item.course_code,
                        "syllabus": item.syllabus_item
                    }
                    response = requests.post(f"{ai_server_url}/api/syllabus", json=syllabus_data)
                    response.raise_for_status()
                logger.info(f"Syllabus sent for course: {course_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to send syllabus for course {course_code}: {str(e)}")
                results["syllabus"] = f"error: {str(e)}"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 4. Questions
            try:
                questions = CourseQuestion.objects.filter(course_code=course_code)
                if not questions:
                    logger.error(f"No questions found for course: {course_code}")
                    results["questions"] = "error: No questions found"
                    return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_400_BAD_REQUEST)
                for question in questions:
                    question_data = {
                        "course_code": question.course_code,
                        "questions": question.question
                    }
                    response = requests.post(f"{ai_server_url}/api/questions", json=question_data)
                    response.raise_for_status()
                logger.info(f"Questions sent for course: {course_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to send questions for course {course_code}: {str(e)}")
                results["questions"] = f"error: {str(e)}"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 5. Course Materials
            try:
                materials = CourseMaterial.objects.filter(course_code=course_code)
                if not materials:
                    logger.error(f"No materials found for course: {course_code}")
                    results["materials"] = "error: No materials found"
                    return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_400_BAD_REQUEST)
                for material in materials:
                    # Decode URL-encoded characters and strip leading '/' to get correct file path
                    file_name = urllib.parse.unquote(os.path.basename(material.file_path))
                    file_path = os.path.join('media', file_name)
                    if not os.path.exists(file_path):
                        logger.error(f"File not found for course {course_code}: {file_path}")
                        results["materials"] = f"error: File not found - {file_path}"
                        return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_400_BAD_REQUEST)
                    with open(file_path, 'rb') as f:
                        encoder = MultipartEncoder(
                            fields={
                                'course_code': material.course_code,
                                'file_type': material.file_type,
                                'file': (file_name, f, 'application/octet-stream')
                            }
                        )
                        headers = {'Content-Type': encoder.content_type}
                        response = requests.post(f"{ai_server_url}/api/course_materials", data=encoder, headers=headers)
                        response.raise_for_status()
                logger.info(f"Materials sent for course: {course_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to send materials for course {course_code}: {str(e)}")
                results["materials"] = f"error: {str(e)}"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            # 6. Trigger Final Processing
            try:
                response = requests.post(f"{ai_server_url}/api/process_file", json={"course_code": course_code})
                response.raise_for_status()
                logger.info(f"Final processing triggered for course: {course_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to trigger processing for course {course_code}: {str(e)}")
                results["trigger"] = f"error: {str(e)}"
                return Response({"course_code": course_code, "status": "failed", "results": results}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # All steps successful
            return Response({
                "course_code": course_code,
                "status": "processing_started",
                "results": results
            }, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            logger.error(f"Course not found: {course_code}")
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)


def list_users(request):
    permission_classes = [IsAuthenticated] 
    users = AdminAppUser.objects.all()  # Fetch all users from the shared table
    user_data = []
    
    for index, user in enumerate(users, start=1):
        user_data.append({
            
            'index': index,  # Serial number starting from 1
            'id': user.id,  # User ID
            'name': user.full_name,
            'phone number': user.phone_number ,
            'year of study': user.year_of_study,
            'status': user.status,
        })
    return JsonResponse({'users': user_data}, status=200)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ToggleUserStatus(View):
    permission_classes = []

    def post(self, request, user_id):
        try:
            # Query using the custom `id` field instead of `_id`
            user = AdminAppUser.objects.get(id=user_id)  # Query by `id`

            # Toggle the user's status using a conditional expression
            user.status = 'accepted' if user.status == 'rejected' else 'rejected'
            user.save()

            return JsonResponse({"message": f"User status updated to {user.status}"}, status=200)
        except AdminAppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except AdminAppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        
from django.shortcuts import get_object_or_404  
from django.http import JsonResponse

def view_user_details(request, user_id):
    # Query using the custom `id` field
    user = get_object_or_404(AdminAppUser, id=user_id)  # Query by `id` instead of `_id`

    user_details = {
        'name': user.full_name,
        'phone_number': user.phone_number,
        'email': user.email,  # Include email
        'year_of_study': user.year_of_study,  # Include year of study
        'college': user.college,
        'department': user.department,
        'university': user.university,
        'blood_group': user.blood_group,
        'profile_pic': user.profile_pic.url if user.profile_pic else None,
        'subscription_plan': user.subscription_plan,
        'status': user.status
    }

    return JsonResponse({'user': user_details}, status=200)