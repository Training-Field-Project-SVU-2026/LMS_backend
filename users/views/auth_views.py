from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from users.models import User
from users.serializers import StudentRegisterSerializer,LoginSerializer

#==============================student register=============================
class StudentRegisterView(APIView):
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            verification_link = f"http://127.0.0.1:8000/users/verify/{user.verification_token}/"

            send_mail(
                subject="Verify Your Email",
                message=f"Click this link to verify your account:\n{verification_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            return Response(
                {
                    "message": "Student registered successfully. Please verify your email.",
                    "student": {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "role": user.role,
                        "slug": user.slug,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    #====================verify email==================
    
class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)

            if user.is_verified:
                return Response({"message": "Email already verified"})

            user.is_verified = True
            user.verification_token = None  
            user.save()

            return Response({"message": "Email verified successfully"})

        except User.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)
        
#============login for users================= 
    
class UserLogin(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user_obj']
        access = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']

        return Response({
            "message": "Login successful",
            "access": access,
            "refresh": refresh,
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
                "slug":user.slug
               
            }
        }, status=status.HTTP_200_OK)