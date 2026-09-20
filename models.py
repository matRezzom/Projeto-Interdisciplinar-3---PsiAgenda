from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Psicologo(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_psicologo')
    nome_completo = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    crp = models.CharField(max_length=20, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    endereco = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr(a). {self.nome_completo} (CRP: {self.crp})"


class Paciente(models.Model):
    nome_completo = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_completo


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]

    psicologo = models.ForeignKey(Psicologo, on_delete=models.PROTECT, related_name='agendamentos')
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='agendamentos')
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AGENDADO')
    observacao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validação para impedir dois agendamentos no mesmo horário para o mesmo psicólogo
        if self.status == 'AGENDADO':
            conflito = Agendamento.objects.filter(
                psicologo=self.psicologo,
                data_hora=self.data_hora,
                status='AGENDADO'
            ).exclude(pk=self.pk)

            if conflito.exists():
                raise ValidationError('Este psicólogo já possui uma consulta marcada para este dia e horário.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paciente.nome_completo} - {self.psicologo.nome_completo} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"