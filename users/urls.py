from django.urls import path
from .views.auth_views import ResetPasswordView, StudentRegisterView, UserLogout,VerifyEmailView,UserLogin,ForgotPasswordView
from .views.student_views import StudentDetailView, StudentListView
from .views.instructor_views import InstructorCreateView, InstructorListView,InstructorDetailView
urlpatterns = [
  #==============================auth urls=============================
    path('register/student/', StudentRegisterView.as_view(), name='student-register'),
      path('verify/<uuid:token>/', VerifyEmailView.as_view()),
      path('login/',UserLogin.as_view(),name='login'),
      path('logout/',UserLogout.as_view(),name='logout'),
      path('forgot-password/',ForgotPasswordView.as_view(),name='forgot_password'),
      path('reset-password/',ResetPasswordView.as_view(),name='reset_password'), 
    ################################student urls############################    
      path('students',StudentListView.as_view(),name="all_students"),
      path('students/<slug:slug>/',StudentDetailView.as_view(),name="student_detail"),
      ################################instructor urls############################
      path('instructors/create/',InstructorCreateView.as_view(),name="create_instructor"),
     path('instructors/',InstructorListView.as_view(),name="all_instructors"),
     path('instructors/<slug:slug>/',InstructorDetailView.as_view(),name="instructor_detail"),
    
]