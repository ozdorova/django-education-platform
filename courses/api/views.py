from rest_framework import generics
from courses.models import Subject
from courses.api.serializers import SubjectSerializer


class SubjectListView(generics.ListAPIView):
    """API представление предметов"""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    """API представление предмета одного предмета, по ключу pk"""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
