from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from courses.models import Subject, Course
from courses.api.serializers import SubjectSerializer, CourseSerializer
from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from courses.api.permissions import IsEnrolled
from courses.api.serializers import CourseWithContentsSerializer


class SubjectListView(generics.ListAPIView):
    """API представление предметов"""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    """API представление предмета одного предмета, по ключу pk"""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


# class CourseEnrollView(APIView):
#     """API представление для записи студентов на курсы"""

#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk, format=None):
#         """POST"""
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset представление курсов только для чтения """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True, methods=['post'], authentication_classes=[BasicAuthentication], permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        """Функция записи студента на курс"""
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})

    @action(detail=True, methods=['get'], serializer_class=CourseWithContentsSerializer, authentication_classes=[BasicAuthentication], permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        """Возвращает обьект Course, если студент записан на курс"""
        return self.retrieve(request, *args, **kwargs)
