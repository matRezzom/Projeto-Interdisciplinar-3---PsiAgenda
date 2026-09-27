from django import forms
from django.contrib.auth.models import User
from .models import Agendamento, Paciente, Psicologo

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['psicologo', 'paciente', 'data_hora', 'observacao']
        widgets = {
            'psicologo': forms.Select(attrs={'class': 'form-select'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Anotações administrativas...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        psicologo = cleaned_data.get('psicologo')
        data_hora = cleaned_data.get('data_hora')

        if psicologo and data_hora:
            # Verifica choque de horários apenas para agendamentos ativos
            agendamentos_existentes = Agendamento.objects.filter(
                psicologo=psicologo, 
                data_hora=data_hora, 
                status='AGENDADO'
            )
            # Se for uma edição, exclui o próprio agendamento da verificação
            if self.instance.pk:
                agendamentos_existentes = agendamentos_existentes.exclude(pk=self.instance.pk)

            if agendamentos_existentes.exists():
                self.add_error('data_hora', 'O horário selecionado já está ocupado para este psicólogo.')
        
        return cleaned_data


class PacienteForm(forms.ModelForm):
    username = forms.CharField(
        label="Nome de Usuário (para Login)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: joao.silva'})
    )
    senha_provisoria = forms.CharField(
        label="Senha Provisória",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crie uma senha temporária'}),
        help_text="O paciente precisará alterar esta senha no primeiro login."
    )

    class Meta:
        model = Paciente
        fields = ['nome_completo', 'cpf', 'data_nascimento', 'telefone', 'email', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username


class EditarPacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome_completo', 'cpf', 'data_nascimento', 'telefone', 'email', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PsicologoForm(forms.ModelForm):
    username = forms.CharField(
        label="Nome de Usuário (para Login)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: psico.ana'})
    )
    senha_provisoria = forms.CharField(
        label="Senha Provisória",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crie uma senha temporária'}),
        help_text="O psicólogo precisará desta senha para realizar o primeiro acesso."
    )

    class Meta:
        model = Psicologo
        fields = ['nome_completo', 'crp', 'cpf', 'data_nascimento', 'telefone', 'email', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'crp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CRP 00/00000'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username


class EditarPsicologoForm(forms.ModelForm):
    class Meta:
        model = Psicologo
        fields = ['nome_completo', 'crp', 'cpf', 'data_nascimento', 'telefone', 'email', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'crp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CRP 00/00000'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }