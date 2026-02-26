
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User,Student
from users.serializers import StudentSerializer, StudentUpdateSerializer, StudentUpdateSerializer
#=====================all students=========================
class StudentListView(APIView):
    def get(self, request):
        students = Student.objects.select_related("user").all()
        serializer = StudentSerializer(students, many=True)
        return Response(
            {
                "message": "Students retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


# ================= update/ delete/ profile student =================
class StudentDetailView(APIView):

    def get_object(self, slug):
        return Student.objects.select_related("user").filter(user__slug=slug).first()
## student profile
    def get(self, request, slug):
        student = self.get_object(slug)
        if not student:
            return Response(
                {"message": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentSerializer(student)
        return Response(
            {"message": "Student retrieved successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def put(self, request, slug):
        student = self.get_object(slug)
        if not student:
            return Response(
                {"message": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Student updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        student = self.get_object(slug)
        if not student:
            return Response(
                {"message": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(
            {"message": "Student deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )