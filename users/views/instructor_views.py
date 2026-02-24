from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import Instructor
from users.serializers import InstructorSerializer, InstructorUpdateSerializer

class InstructorListView(APIView):
     def get(self, request):
        instructors = Instructor.objects.select_related("user").all()
        serializer = InstructorSerializer(instructors, many=True)
        return Response(
            {
                "message": "Instructors retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
# ================= profile / update / delete  instructor=================
class InstructorDetailView(APIView):

    def get_object(self, slug):
        return Instructor.objects.select_related("user").filter(user__slug=slug).first()

    def get(self, request, slug):
        instructor = self.get_object(slug)
        if not instructor:
            return Response(
                {"message": "Instructor not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = InstructorSerializer(instructor)
        return Response(
            {"message": "Instructor retrieved successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def put(self, request, slug):
        instructor = self.get_object(slug)
        if not instructor:
            return Response(
                {"message": "Instructor not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = InstructorUpdateSerializer(instructor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Instructor updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        instructor = self.get_object(slug)
        if not instructor:
            return Response(
                {"message": "Instructor not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        instructor.delete()
        return Response(
            {"message": "Instructor deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )