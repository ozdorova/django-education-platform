from rest_framework import serializers
from courses.models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subject"""
    class Meta:
        model = Subject
        fields = [
            'id', 'title', 'slug',
        ]
