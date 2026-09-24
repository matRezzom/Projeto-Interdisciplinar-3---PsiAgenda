from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AgendamentoForm
from django.contrib.auth.models import User
from datetime import datetime, date, time
from django.db.models import Q
from django.utils.timezone import make_aware, get_current_timezone

from .models import Agendamento, Psicologo, Paciente, Psicologo
from .forms import PacienteForm, PsicologoForm

def home(request):
    return HttpResponse("Servidor do PsiAgenda rodando com sucesso!")

@login_required
def dashboard_redirect(request):
    """Redireciona o usuário para seu painel específico."""
    if hasattr(request.user, 'perfil_psicologo'):
        return redirect('painel_psicologo')
    else:
        return redirect('painel_secretaria')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from .models import Agendamento

from datetime import datetime, time
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Agendamento

@login_required
def painel_secretaria(request):
    # 1. Captura os parâmetros recebidos da URL / Formulário
    data_str = request.GET.get('data')
    busca = request.GET.get('busca', '').strip()

    # --- INÍCIO DO DEBUG NO TERMINAL ---
    print("\n" + "="*50)
    print(" [DEBUG] NOVA REQUISIÇÃO RECEBIDA")
    print(f" -> GET 'data' recebido: '{data_str}'")
    print(f" -> GET 'busca' recebido: '{busca}'")

    # Quantidade total de agendamentos no banco de dados
    total_bd = Agendamento.objects.count()
    print(f" -> Total de agendamentos salvos no Banco: {total_bd}")

    agendamentos = Agendamento.objects.all()

    # Filtro por busca de texto
    if busca:
        agendamentos = agendamentos.filter(paciente__nome_completo__icontains=busca)
        print(f" -> Após filtrar por nome '{busca}': {agendamentos.count()} resultados")

    # Filtro por data
    if data_str:
        agendamentos = agendamentos.filter(data_hora__startswith=data_str)
        print(f" -> Após filtrar por data '{data_str}': {agendamentos.count()} resultados")

    print(f" -> Resultado final a enviar para a tela: {list(agendamentos)}")
    print("="*50 + "\n")
    # --- FIM DO DEBUG ---

    context = {
        'agendamentos': agendamentos,
        'data_selecionada': data_str if data_str else '',
        'busca': busca,
    }
    return render(request, 'agendamentos/painel_secretaria.html', context)

@login_required
def painel_psicologo(request):
    """Painel do Psicólogo: mostra apenas a própria agenda."""
    try:
        psicologo = request.user.perfil_psicologo
        hoje = timezone.now().date()
        minhas_consultas = Agendamento.objects.filter(psicologo=psicologo, data_hora__date=hoje).order_by('data_hora')
    except Psicologo.DoesNotExist:
        minhas_consultas = []
    return render(request, 'agendamentos/painel_psicologo.html', {'agendamentos': minhas_consultas})

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
            
            # Gera um nome de utilizador baseado no e-mail ou CPF
            username = psicologo.email.split('@')[0]
            
            # Verifica se já existe um utilizador com esse username, se sim, ajusta
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.count()}"
            
            # Cria a conta de utilizador para o psicólogo aceder ao sistema
            novo_usuario = User.objects.create_user(
                username=username,
                email=psicologo.email,
                password='senha_padrao_psicologo'  # O psicólogo pode alterar depois
            )
            
            # Vincula o utilizador criado ao psicólogo
            psicologo.usuario = novo_usuario
            psicologo.save()
            
            messages.success(request, f'Psicólogo cadastrado com sucesso! Utilizador de acesso: {username}')
            return redirect('listar_psicologos')
    else:
        form = PsicologoForm()
    return render(request, 'agendamentos/cadastrar_psicologo.html', {'form': form})