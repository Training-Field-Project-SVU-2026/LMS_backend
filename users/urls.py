from django.urls import path
from .views.auth_views import StudentRegisterView,VerifyEmailView,UserLogin
from .views.student_views import StudentDetailView, StudentListView
from .views.instructor_views import InstructorListView,InstructorDetailView
urlpatterns = [
    path('register/student/', StudentRegisterView.as_view(), name='student-register'),
      path('verify/<uuid:token>/', VerifyEmailView.as_view()),
      path('login/',UserLogin.as_view(),name='login'),
      path('students',StudentListView.as_view(),name="all_students"),
      path('students/<slug:slug>/',StudentDetailView.as_view(),name="student_detail"),
     path('instructors/',InstructorListView.as_view(),name="all_instructors"),
     path('instructors/<slug:slug>/',InstructorDetailView.as_view(),name="instructor_detail"),
    
]