from django.contrib import admin
from django.urls import path
from agendamentos import views

urlpatterns = [
    # --- ADMIN DO DJANGO ---
    path('admin/', admin.site.urls),

    # --- PÁGINA INICIAL E AUTENTICAÇÃO ---
    path('', views.dashboard_redirect, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.fazer_logout, name='logout'),

    # --- PAINÉIS / DASHBOARDS ---
    path('secretaria/', views.painel_secretaria, name='painel_secretaria'),
    path('psicologo/', views.painel_psicologo, name='painel_psicologo'),
    path('paciente/', views.painel_paciente, name='painel_paciente'),

    # --- AGENDAMENTOS ---
    path('agendamentos/novo/', views.criar_agendamento, name='criar_agendamento'),
    path('agendamento/<int:agendamento_id>/editar/', views.editar_agendamento, name='editar_agendamento'),
    path('agendamento/<int:agendamento_id>/cancelar/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('secretaria/confirmar-notificacao/<int:agendamento_id>/', views.confirmar_notificacao, name='confirmar_notificacao'),

    # --- GESTÃO DE PACIENTES ---
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('pacientes/novo/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('pacientes/<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:pk>/deletar/', views.deletar_paciente, name='deletar_paciente'),

    # --- GESTÃO DE PSICÓLOGOS ---
    path('psicologos/', views.listar_psicologos, name='listar_psicologos'),
    path('psicologos/novo/', views.cadastrar_psicologo, name='cadastrar_psicologo'),
    path('psicologos/<int:pk>/editar/', views.editar_psicologo, name='editar_psicologo'),
    path('psicologos/<int:pk>/deletar/', views.deletar_psicologo, name='deletar_psicologo'),

    path('psicologo/consulta/<int:pk>/solicitar-cancelamento/', views.solicitar_cancelamento_psicologo, name='solicitar_cancelamento_psicologo'),
]