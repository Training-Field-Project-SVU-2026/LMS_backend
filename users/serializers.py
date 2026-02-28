
from django.conf import settings
from rest_framework import serializers
from .models import PasswordResetOtp, User, Student,Instructor
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail 
from django.utils.crypto import get_random_string
 
class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)  

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'is_active', 'is_verified', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role='student'
        )
        user.save()
        student= Student.objects.create(user=user)
        return user
    
    
    #############login ################
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user_obj = None 

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_verified:
            raise serializers.ValidationError("Email is not verified")

        if not user.is_active:
            raise serializers.ValidationError("Account is inactive")

        refresh = RefreshToken.for_user(user)
        attrs['access'] = str(refresh.access_token)
        attrs['refresh'] = str(refresh)
        attrs['user_obj'] = user  
        
        return attrs
    
    ##########student#############
class StudentSerializer(serializers.ModelSerializer):
     email = serializers.CharField(source="user.email", read_only=True)
     first_name = serializers.CharField(source="user.first_name", read_only=True)
     last_name = serializers.CharField(source="user.last_name", read_only=True)
     slug = serializers.CharField(source="user.slug", read_only=True)
     is_verified =serializers.BooleanField(source="user.is_verified",read_only=True)
     image = serializers.ImageField(source="user.image", read_only=True)
     
     class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'slug','is_verified','image']
        
        ####UpdateSerializer for student profile

class StudentUpdateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    image = serializers.ImageField(source="user.image")

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'image']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.image = user_data.get('image', user.image)
        user.save()

        instance.save()
        return instance
        
        
        ###################instructor####################
class InstructorSerializer(serializers.ModelSerializer):
     email = serializers.CharField(source="user.email", read_only=True)
     first_name = serializers.CharField(source="user.first_name", read_only=True)
     last_name = serializers.CharField(source="user.last_name", read_only=True)
     slug = serializers.CharField(source="user.slug", read_only=True)
     image = serializers.ImageField(source="user.image", read_only=True)
        
     class Meta:
        model = Instructor
        fields = ['first_name', 'last_name', 'email', 'slug','bio','description','image']
        
        ##====================update instructor========================
class InstructorUpdateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    image = serializers.ImageField(source="user.image")
    bio = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Instructor
        fields = ['first_name', 'last_name', 'email', 'image', 'bio', 'description']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.image = user_data.get('image', user.image)
        user.save()

        instance.bio = validated_data.get('bio', instance.bio)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
    
    
#=====================create instructor========================

class InstructorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    # validate email
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def create(self, validated_data):
        password = get_random_string(length=8)

        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role='instructor',
            password=password
        )
        user.is_verified = True
        user.save()

        instructor = Instructor.objects.create(user=user)

        send_mail(
            subject="Instructor Account Created",
            message=f"""
Hello {user.first_name},

Your instructor account has been created.

Email: {user.email}
Temporary Password: {password}

Please change your password after login.
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )

        return instructor
    
    
# ================= Forget Password Serializer =================
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

# ================= Reset Password Serializer =================
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")
        new_password = attrs.get("new_password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

        
        try:
            otp_record = PasswordResetOtp.objects.get(email=email, otp=otp)
        except PasswordResetOtp.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        
        if otp_record.is_expired():
            otp_record.delete()  
            raise serializers.ValidationError("OTP has expired.")

        attrs['user'] = user
        attrs['otp_record'] = otp_record
        return attrs
        
       

    