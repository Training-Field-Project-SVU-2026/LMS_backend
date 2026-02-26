
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from users.models import User
from users.serializers import StudentRegisterSerializer, LoginSerializer, ForgetPasswordSerializer, ResetPasswordSerializer
from users.models import PasswordResetOtp, User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

#==============================student register=============================
class StudentRegisterView(APIView):
    def post(self, request):
        serializer =StudentRegisterSerializer(data=request.data)

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
        
        
        # ================logout=============
        
class UserLogout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        

# ================== Forgot Password ==================
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        
        otp = str(uuid.uuid4().int)[:6]

        PasswordResetOtp.objects.create(email=email, otp=otp)

        send_mail(
            subject="Password Reset OTP",
            message=f"Your OTP for password reset is: {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)


# ================== Reset Password ==================
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp_record = serializer.validated_data['otp_record']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        otp_record.delete()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)