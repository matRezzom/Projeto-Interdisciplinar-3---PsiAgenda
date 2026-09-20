from django.contrib import admin

from django.contrib import admin
from .models import Psicologo, Paciente, Agendamento

@admin.register(Psicologo)
class PsicologoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'crp', 'cpf', 'telefone', 'ativo')
    search_fields = ('nome_completo', 'cpf', 'crp')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'telefone', 'ativo')
    search_fields = ('nome_completo', 'cpf')

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'psicologo', 'data_hora', 'status')
    list_filter = ('status', 'psicologo', 'data_hora')
    search_fields = ('paciente__nome_completo', 'psicologo__nome_completo')
