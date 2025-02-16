from django.core.mail import send_mail as send
from django.template.loader import render_to_string

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

import resend

from django_snippets.settings import RESEND_API_KEY


resend.api_key = RESEND_API_KEY

def send_email(subject: str, recipient_list: list[str], template: str, context: dict[str, str]):
    try:
        html = render_to_string(template, context)
        
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": recipient_list,
            "subject": subject,
            "html": html,
        })

        return response
    except Exception as e:
        print(e)
        return  e


def get_snippet_format(snippet: str, language: str):
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter(style="emacs")
    result = highlight(snippet, lexer, formatter)

    return result