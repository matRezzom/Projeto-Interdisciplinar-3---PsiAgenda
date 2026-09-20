from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AgendamentoForm

def criar_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta agendada com sucesso!')
            return redirect('home_secretaria')
    else:
        form = AgendamentoForm()

    return render(request, 'agendamentos/novo.html', {'form': form})