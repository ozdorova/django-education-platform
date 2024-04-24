from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View
from django.urls import reverse_lazy
from .forms import ModuleFormSet
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class OwnerMixin:
    """Миксин переопределяющий queryset, чтобы извлекать обьекты принадлежащие текущему пользователю"""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    """Миксин для использования в представлениях с формами, чтобы сохранять курс за текущим пользователем"""

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    """Миксин определяющий модель, поля и перенаправление"""
    model = Course
    fields = [
        'subject', 'title', 'slug', 'overview',
    ]
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """Миксин для редактирования курса. Create и Update"""
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    """Представление всех курсов текущего пользователя"""
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """Представлене создание курса"""
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """Представление изменения курса"""
    permission_required = 'course.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """Представление удаления курса"""
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """Представление набора форм, для добавления, обновления и удаления модулей определенного курса"""

    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        """Получение набора форм для определенного курса"""
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        """метод делегирования запроса и параметров запроса методам класса"""
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        """GET"""
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        """POST"""
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})
