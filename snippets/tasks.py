from .utils import send_email

def sendEmailInSnippetCreation(snippet):
    subject = 'Snippet "' + snippet.name + '" created successfully'
    user_mail = snippet.user.email

    if user_mail:
        sended = send_email(
            subject=subject,
            recipient_list=[user_mail],
            template='email/snippet_mail.html',
            context={
                "user": snippet.user,
                "snippet": snippet,
            }
        )
