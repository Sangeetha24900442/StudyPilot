"""
URL configuration for notes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pilot.views import material_answer
from pilot.views import quiz_page, generate_quiz,quiz_result


from pilot.views import home, login_page, register_page, dashboard, chatbot, chat_page, upload_material,material_view


urlpatterns = [

    path("admin/", admin.site.urls),

    path("", home, name="home"),
    path("home/", home, name="home"),

    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),

    path('upload/',upload_material,name='upload'),
    path("materials/", material_view, name="material_view"),


    path("dashboard/", dashboard, name="dashboard"),
    path("chatbot/", chatbot),
    path("chat/", chat_page),
    path("material/answer/", material_answer, name="material_answer"),
    path("quiz/", quiz_page, name="quiz"),
    path("quiz/data/", generate_quiz, name="generate_quiz"),
    path("quiz/<int:material_id>/", quiz_page, name="quiz"),
    path("quiz/<int:material_id>/data/",generate_quiz,name="generate_quiz"),
    path("quiz/<int:material_id>/result/", quiz_result, name="quiz_result"),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
