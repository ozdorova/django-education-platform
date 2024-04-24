from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Course


class OwnerMixin:
    """Миксин переопределяющий queryset, чтобы извлекать обьекты принадлежащие текущему пользователю"""

    def get_queryser(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    """Миксин для использования в представлениях с формами, чтобы сохранять курс за текущим пользователем"""

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin):
    """Миксин определяющий модель, поля и перенаправление"""
    model = Course
    fields = [
        'subject', 'title', 'slug', 'overview',
    ]
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """Миксин для редактирования курса. Create и Update"""
    template_name = 'course/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    """Представление всех курсов текущего пользователя"""
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """Представлене создание курса"""
    pass


class CourseUpdateMixin(OwnerCourseEditMixin, UpdateView):
    """Представление изменения курса"""
    pass


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """Представление удаления курса"""
    template_name = 'course/manage/course/delete.html'
