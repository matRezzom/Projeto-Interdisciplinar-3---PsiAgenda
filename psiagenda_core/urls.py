from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from agendamentos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_redirect, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='agendamentos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('secretaria/', views.painel_secretaria, name='painel_secretaria'),
    path('psicologo/', views.painel_psicologo, name='painel_psicologo'),
    path('agendamentos/novo/', views.criar_agendamento, name='criar_agendamento'),
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('pacientes/novo/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('psicologos/', views.listar_psicologos, name='listar_psicologos'),
    path('psicologos/novo/', views.cadastrar_psicologo, name='cadastrar_psicologo'),
]