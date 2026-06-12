from django.core.mail import send_mail
from django.conf import settings


def send_reset_email(email: str, reset_url: str):
    send_mail(
            subject='Redefinição de senha - Onboarding Grupo Enriquecedor',
            message=f'Acesse o link para redefinir sua senha: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=f'<p>Clique no link para redefinir sua senha:</p><p><a href="{reset_url}">{reset_url}</a></p><p>O link expira em 24 horas.</p>',
            fail_silently=True
        )