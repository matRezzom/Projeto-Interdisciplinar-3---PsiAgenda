from django import forms
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

class PacienteForm(forms.ModelForm):
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
    class Meta:
        model = Psicologo
        fields = ['nome_completo', 'cpf', 'crp', 'data_nascimento', 'telefone', 'email', 'endereco']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'crp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00/00000'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        psicologo = cleaned_data.get('psicologo')
        data_hora = cleaned_data.get('data_hora')

        if psicologo and data_hora:
            if Agendamento.objects.filter(psicologo=psicologo, data_hora=data_hora, status='AGENDADO').exists():
                self.add_error('data_hora', 'O horário selecionado já está ocupado para este psicólogo.')
        
        return cleaned_data