from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from .forms import ModuleFormSet
from .models import Course, Module, Content, Subject
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.apps import apps
from django.forms.models import modelform_factory
from braces.views import CsrfExemptMixin, JSONRequestResponseMixin
from django.db.models import Count
from students.forms import CourseEnrollForm


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


class ContentCreateUpdateView(TemplateResponseMixin, View):
    """Представление изменения содержимого модулей"""

    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        """Полученик модели по допустимому имени класса"""

        if model_name in ['text', 'video', 'image', 'file']:
            # получение фактического класса для имени model_name
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        """Создане динамической формы с помощью model_form_factory"""

        # Исключаем из динамических форм поля owner, order, created, uodated
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        """При обработке запроса метод добавляет атрибуты module, obj и model в экземпляр"""
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        """GET"""

        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        """POST"""

        form = self.get_form(self.model, instance=self.obj,
                             data=request.POST, files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # новое содержимое модуля
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    """Удаление содержимого"""

    def post(self, request, id):
        """POST"""

        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user)

        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    """Представление отображения всех модулей курса"""

    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        """GET"""

        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JSONRequestResponseMixin, View):
    """Представление для изменения порядка следования модулей"""

    def post(self, request):
        """POST"""
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JSONRequestResponseMixin, View):
    """Представление для изменения порядка следования содержимого"""

    def post(self, request):
        """POST"""
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    """Вывод списка всех доступных курсов"""

    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        """GET"""
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))

        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response({'subjects': subjects, 'subject': subject, 'courses': courses})


class CourseDetailView(DetailView):
    """Представлении информации о конкретном курсе"""

    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object})
        return context
