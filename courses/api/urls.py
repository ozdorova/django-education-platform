from django.urls import path, include
from rest_framework import routers
from . import views


app_name = 'courses'

# создание маршрутизатора и регистрация viewset
router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)


urlpatterns = [
    path('subjects/', views.SubjectListView.as_view(), name='suject_list'),
    path('subjects/<pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('courses/<pk>/enroll/',
         views.CourseEnrollView.as_view(), name='course_enroll'),
    path('', include(router.urls))
]
