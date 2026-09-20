from django import forms
from .models import Agendamento, Paciente, Psicologo

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['psicologo', 'paciente', 'data_hora', 'observacao']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        psicologo = cleaned_data.get('psicologo')
        data_hora = cleaned_data.get('data_hora')

        if psicologo and data_hora:
            if Agendamento.objects.filter(psicologo=psicologo, data_hora=data_hora, status='AGENDADO').exists():
                self.add_error('data_hora', 'O horário selecionado já está ocupado para este psicólogo.')
        
        return cleaned_data