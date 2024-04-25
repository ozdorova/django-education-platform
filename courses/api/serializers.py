from rest_framework import serializers
from courses.models import Subject, Course, Module, Content


class SubjectSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subject"""
    class Meta:
        model = Subject
        fields = [
            'id', 'title', 'slug',
        ]


class ModuleSerializer(serializers.ModelSerializer):
    """Сериализатор модели Module"""
    class Meta:
        model = Module
        fields = [
            'order', 'title', 'description',
        ]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор модели Course"""

    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'subject', 'title', 'slug',
            'overview', 'created', 'owner', 'modules',
        ]


class ItemRelatedField(serializers.RelatedField):
    """Сериализатор рендера содержимого"""

    def to_representation(self, value):
        return value.render()


class ContentSerializer(serializers.ModelSerializer):
    """Сериализатор содежимого модулей"""

    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = [
            'order', 'item',
        ]


class ModuleWithContentSerializer(serializers.ModelSerializer):
    """Сериализатор модуля с содержимым"""

    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = [
            'order', 'title', 'description', 'contents',
        ]


class CourseWithContentsSerializer(serializers.ModelSerializer):
    """Сериализатор Курса с содержимым"""

    modules = ModuleWithContentSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            'id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'modules',
        ]
