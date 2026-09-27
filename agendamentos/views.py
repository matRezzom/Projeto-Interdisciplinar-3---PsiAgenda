from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import get_current_timezone, make_aware

from .forms import AgendamentoForm, PacienteForm, PsicologoForm
from .models import Agendamento, Paciente, Psicologo


# --- HOME E REDIRECIONAMENTOS DE AUTENTICAÇÃO ---
def home(request):
    return HttpResponse("Servidor do PsiAgenda rodando com sucesso!")


class CustomLoginView(LoginView):
    template_name = 'agendamentos/login.html'

    def get_success_url(self):
        user = self.request.user

        # 1. Se for Superusuário / Admin / Secretária
        if user.is_superuser or user.is_staff:
            return '/secretaria/'

        # 2. Se for Psicólogo (possui perfil associado)
        if hasattr(user, 'perfil_psicologo'):
            return '/psicologo/'

        # 3. Se for Paciente (cadastrado com o mesmo e-mail)
        if Paciente.objects.filter(email=user.email).exists():
            return '/paciente/'

        return '/secretaria/'


def fazer_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    """Redireciona o usuário para seu painel específico."""
    if hasattr(request.user, 'perfil_psicologo'):
        return redirect('painel_psicologo')
    elif Paciente.objects.filter(email=request.user.email).exists():
        return redirect('painel_paciente')
    else:
        return redirect('painel_secretaria')


# --- PAINEL DA SECRETÁRIA ---
@login_required
def painel_secretaria(request):
    data_str = request.GET.get('data', '').strip()
    busca = request.GET.get('busca', '').strip()

    hoje = date.today()
    amanha = hoje + timedelta(days=1)

    # Base de todos os agendamentos ativos
    agendamentos = Agendamento.objects.filter(status='AGENDADO').order_by('data_hora')

    # Filtra por data APENAS se a secretária escolheu uma data específica
    if data_str:
        agendamentos = agendamentos.filter(data_hora__date=data_str)

    # Filtra por nome se foi digitado algo na busca
    if busca:
        agendamentos = agendamentos.filter(paciente__nome_completo__icontains=busca)

    # Notificações de amanhã que ainda não foram confirmadas (RF08)
    notificacoes_amanha = Agendamento.objects.filter(
        data_hora__date=amanha, 
        status='AGENDADO'
    ).order_by('data_hora')

    context = {
        'agendamentos': agendamentos,
        'notificacoes_amanha': notificacoes_amanha,
        'data_selecionada': data_str,
        'busca': busca,
        'amanha': amanha,
    }
    return render(request, 'agendamentos/painel_secretaria.html', context)


@login_required
def confirmar_notificacao(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.notificacao_confirmada = True
    agendamento.save()
    return redirect('painel_secretaria')


# --- GESTÃO DE AGENDAMENTOS ---
@login_required
def criar_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta agendada com sucesso!')
            return redirect('painel_secretaria')
    else:
        form = AgendamentoForm()

    return render(request, 'agendamentos/criar_agendamento.html', {'form': form})


@login_required
def editar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta atualizada com sucesso!')
            return redirect('painel_secretaria')
    else:
        form = AgendamentoForm(instance=agendamento)
        
    return render(request, 'agendamentos/editar.html', {
        'form': form,
        'agendamento': agendamento
    })


@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if request.method == 'POST':
        agendamento.status = 'CANCELADO'
        agendamento.save()
        messages.success(request, f'Consulta de {agendamento.paciente.nome_completo} foi cancelada e o horário está livre.')
        return redirect('painel_secretaria')
        
    return render(request, 'agendamentos/confirmar_cancelamento.html', {
        'agendamento': agendamento
    })


# --- PACIENTES ---
@login_required
def listar_pacientes(request):
    pacientes = Paciente.objects.filter(ativo=True).order_by('nome_completo')
    return render(request, 'agendamentos/listar_pacientes.html', {'pacientes': pacientes})


@login_required
def cadastrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente cadastrado com sucesso!')
            return redirect('listar_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'agendamentos/cadastrar_paciente.html', {'form': form})


@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do paciente atualizados com sucesso!')
            return redirect('listar_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'agendamentos/form_paciente.html', {'form': form, 'titulo': 'Editar Paciente'})


@login_required
def deletar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente excluído com sucesso!')
        return redirect('listar_pacientes')
    return render(request, 'agendamentos/confirmar_deletar.html', {'item': paciente.nome_completo, 'tipo': 'Paciente', 'voltar_url': 'listar_pacientes'})


# --- PSICÓLOGOS ---
@login_required
def listar_psicologos(request):
    psicologos = Psicologo.objects.filter(ativo=True).order_by('nome_completo')
    return render(request, 'agendamentos/listar_psicologos.html', {'psicologos': psicologos})


@login_required
def cadastrar_psicologo(request):
    if request.method == 'POST':
        form = PsicologoForm(request.POST)
        if form.is_valid():
            psicologo = form.save(commit=False)
            
            # Gera um nome de utilizador baseado no e-mail
            username = psicologo.email.split('@')[0]
            
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.count()}"
            
            # Cria a conta de utilizador para o psicólogo aceder ao sistema
            novo_usuario = User.objects.create_user(
                username=username,
                email=psicologo.email,
                password='senha_padrao_psicologo'
            )
            
            psicologo.usuario = novo_usuario
            psicologo.save()
            
            messages.success(request, f'Psicólogo cadastrado com sucesso! Utilizador de acesso: {username}')
            return redirect('listar_psicologos')
    else:
        form = PsicologoForm()
    return render(request, 'agendamentos/cadastrar_psicologo.html', {'form': form})


@login_required
def editar_psicologo(request, pk):
    psicologo = get_object_or_404(Psicologo, pk=pk)
    if request.method == 'POST':
        form = PsicologoForm(request.POST, instance=psicologo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do psicólogo atualizados com sucesso!')
            return redirect('listar_psicologos')
    else:
        form = PsicologoForm(instance=psicologo)
    return render(request, 'agendamentos/form_psicologo.html', {'form': form, 'titulo': 'Editar Psicólogo'})


@login_required
def deletar_psicologo(request, pk):
    psicologo = get_object_or_404(Psicologo, pk=pk)
    if request.method == 'POST':
        psicologo.delete()
        messages.success(request, 'Psicólogo excluído com sucesso!')
        return redirect('listar_psicologos')
    return render(request, 'agendamentos/confirmar_deletar.html', {'item': psicologo.nome_completo, 'tipo': 'Psicólogo', 'voltar_url': 'listar_psicologos'})


# --- PAINEL DO PSICÓLOGO ---
@login_required
def painel_psicologo(request):
    try:
        psicologo = request.user.perfil_psicologo
    except AttributeError:
        return render(request, 'agendamentos/erro_perfil.html', {
            'mensagem': 'O seu utilizador não possui um perfil de Psicólogo associado.'
        })

    data_str = request.GET.get('data', '')
    busca = request.GET.get('busca', '')

    agendamentos = Agendamento.objects.filter(psicologo=psicologo)

    if data_str:
        agendamentos = agendamentos.filter(data_hora__date=data_str)
    
    if busca:
        agendamentos = agendamentos.filter(paciente__nome_completo__icontains=busca)

    agendamentos = agendamentos.order_by('data_hora')

    context = {
        'psicologo': psicologo,
        'agendamentos': agendamentos,
        'data_selecionada': data_str,
        'busca': busca,
    }
    return render(request, 'agendamentos/painel_psicologo.html', context)


# --- PAINEL DO PACIENTE ---
@login_required
def painel_paciente(request):
    paciente = Paciente.objects.filter(email=request.user.email).first()

    if not paciente:
        return render(request, 'agendamentos/erro_perfil.html', {
            'mensagem': 'Nenhum perfil de Paciente foi encontrado para o seu e-mail cadastrado.'
        })

    agendamentos = Agendamento.objects.filter(paciente=paciente).order_by('-data_hora')

    context = {
        'paciente': paciente,
        'agendamentos': agendamentos,
    }
    return render(request, 'agendamentos/painel_paciente.html', context)