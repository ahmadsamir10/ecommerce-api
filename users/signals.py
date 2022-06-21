from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework.authtoken.models import Token
from django_rest_passwordreset.signals import reset_password_token_created







@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=None, **kwargs):
    if created:
        Token.objects.create(user=instance)




@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    
    email = reset_password_token.user.email
    print(email)
    
    plaintext = get_template('pwd_reset.txt')
    htmly     = get_template('pwd_reset.html')

    context = {'token': reset_password_token.key}

    subject, from_email, to = 'Password reset', 'ecommerce@mail.com', email
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
