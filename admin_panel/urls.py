from django.urls import path
from .views import AdminLoginView, AddCourseView, ToggleCourseStatusView, GetCoursesView, ContactFormView,EditCourseView #DummyCourseView

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('add-course/', AddCourseView.as_view(), name='add-course'),
    path('toggle-status/<str:pk>/', ToggleCourseStatusView.as_view(), name='toggle-status'),
    path('course-list/', GetCoursesView.as_view(), name='course-list'),
    #path('dummy-course/', DummyCourseView.as_view(), name='dummy-course'),
    path('contact/', ContactFormView.as_view(), name='contact_form'),
    path('edit-course/<str:pk>/', EditCourseView.as_view(), name='edit-course'),
]