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

from .forms import AgendamentoForm, PacienteForm, PsicologoForm, EditarPsicologoForm
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
    """Redireciona o utilizador logado para o painel correto de acordo com o perfil."""
    if Psicologo.objects.filter(usuario=request.user).exists():
        return redirect('painel_psicologo')
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


def cadastrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            senha = form.cleaned_data.get('senha_provisoria')
            
            user = None
            if username and senha:
                user = User.objects.create_user(
                    username=username,
                    password=senha,
                    email=form.cleaned_data.get('email', '')
                )
            
            paciente = form.save(commit=False)
            if user:
                if hasattr(paciente, 'usuario'):
                    paciente.usuario = user
                elif hasattr(paciente, 'user'):
                    paciente.user = user
            paciente.save()
            
            # Corrigido de paciente.nome para paciente.nome_completo
            messages.success(request, f"Paciente {paciente.nome_completo} cadastrado com sucesso!")
            return redirect('listar_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'agendamentos/cadastrar_paciente.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Paciente
from .forms import EditarPacienteForm

def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = EditarPacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados do paciente {paciente.nome_completo} atualizados!")
            return redirect('listar_pacientes')
    else:
        form = EditarPacienteForm(instance=paciente)

    return render(request, 'agendamentos/form_paciente.html', {'form': form, 'paciente': paciente})

def deletar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        nome = paciente.nome_completo
        # Se o paciente tiver conta de usuário vinculada, deleta o usuário (o paciente é deletado em cascata ou manualmente)
        if hasattr(paciente, 'user') and paciente.user:
            paciente.user.delete()
        else:
            paciente.delete()
            
        messages.success(request, f"Paciente {nome} excluído com sucesso!")
        return redirect('listar_pacientes')

    return render(request, 'agendamentos/confirmar_deletar.html', {'paciente': paciente})

# --- PSICÓLOGOS ---
def listar_psicologos(request):
    busca = request.GET.get('busca', '')
    psicologos = Psicologo.objects.all()
    if busca:
        psicologos = psicologos.filter(nome_completo__icontains=busca)
    return render(request, 'agendamentos/listar_psicologos.html', {'psicologos': psicologos, 'busca': busca})

# 2. Cadastrar Psicólogo (cria Utilizador e Perfil)
def cadastrar_psicologo(request):
    if request.method == 'POST':
        form = PsicologoForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            senha = form.cleaned_data['senha_provisoria']
            
            # Cria a conta de utilizador no Django
            user = User.objects.create_user(
                username=username,
                password=senha,
                email=form.cleaned_data.get('email', '')
            )
            
            # Vincula diretamente o utilizador ao campo 'usuario' do modelo
            psicologo = form.save(commit=False)
            psicologo.usuario = user
            psicologo.save()
            
            messages.success(request, f"Psicólogo {psicologo.nome_completo} cadastrado com sucesso!")
            return redirect('listar_psicologos')
    else:
        form = PsicologoForm()
    return render(request, 'agendamentos/cadastrar_psicologo.html', {'form': form})

# 3. Editar Psicólogo
def editar_psicologo(request, pk):
    psicologo = get_object_or_404(Psicologo, pk=pk)
    if request.method == 'POST':
        form = EditarPsicologoForm(request.POST, instance=psicologo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados do psicólogo {psicologo.nome_completo} atualizados!")
            return redirect('listar_psicologos')
    else:
        form = EditarPsicologoForm(instance=psicologo)
    return render(request, 'agendamentos/form_psicologo.html', {'form': form, 'psicologo': psicologo})

# 4. Eliminar Psicólogo
def deletar_psicologo(request, pk):
    psicologo = get_object_or_404(Psicologo, pk=pk)
    if request.method == 'POST':
        nome = psicologo.nome_completo
        if hasattr(psicologo, 'usuario') and psicologo.usuario:
            psicologo.usuario.delete()
        elif hasattr(psicologo, 'user') and psicologo.user:
            psicologo.user.delete()
        else:
            psicologo.delete()
            
        messages.success(request, f"Psicólogo {nome} excluído com sucesso!")
        return redirect('listar_psicologos')

    return render(request, 'agendamentos/confirmar_deletar_psicologo.html', {'psicologo': psicologo})

# --- PAINEL DO PSICÓLOGO ---
@login_required
def painel_psicologo(request):
    """Exibe apenas as consultas do psicólogo logado com link da sala remota."""
    try:
        psicologo = Psicologo.objects.get(usuario=request.user)
    except Psicologo.DoesNotExist:
        messages.error(request, "Perfil de psicólogo não encontrado.")
        return redirect('painel_secretaria')

    # Busca apenas os agendamentos pertencentes a este psicólogo
    agendamentos = Agendamento.objects.filter(psicologo=psicologo).order_by('data_hora')

    context = {
        'psicologo': psicologo,
        'agendamentos': agendamentos,
    }
    return render(request, 'agendamentos/painel_psicologo.html', context)

@login_required
def solicitar_cancelamento_psicologo(request, pk):
    """Permite ao psicólogo enviar uma solicitação de cancelamento com motivo para a secretária."""
    psicologo = get_object_or_404(Psicologo, usuario=request.user)
    agendamento = get_object_or_404(Agendamento, pk=pk, psicologo=psicologo)

    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Sem motivo informado')
        
        # Altera o status da consulta
        if hasattr(agendamento, 'status'):
            agendamento.status = 'Solicitado Cancelamento'
        
        # Registra a justificativa no campo de observação
        if hasattr(agendamento, 'observacao'):
            obs_anterior = agendamento.observacao or ''
            agendamento.observacao = f"[SOLICITAÇÃO DE CANCELAMENTO - DR(A) {psicologo.nome_completo}]: {motivo}\n{obs_anterior}"
            
        agendamento.save()

        messages.success(request, "Solicitação de cancelamento enviada com sucesso para a secretária!")
        return redirect('painel_psicologo')

    return render(request, 'agendamentos/solicitar_cancelamento_psicologo.html', {'agendamento': agendamento})


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