"""
URL configuration for Maestro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from BookWorm.views import home_view
from StudentWorm.views import student_articles
from TeacherWorm.views import add_article

urlpatterns = [
    path("admin/", admin.site.urls),
    path('teacher-worm/', include('TeacherWorm.urls')),
    path('teacher-worm/', add_article, name='add_articles'),
    path('student-worm/', student_articles, name='student_articles'),
    path('student-worm/', include('StudentWorm.urls')),
    path('', home_view, name='home'),  # Map the root URL to the home_view
]
