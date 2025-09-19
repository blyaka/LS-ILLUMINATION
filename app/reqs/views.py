from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site

from django.core.files.uploadhandler import MemoryFileUploadHandler
from .upload_handlers import MaxSizeUploadHandler

from .forms import RequestForm
from .models import Request, ReqsRecipient

import threading
import logging
log = logging.getLogger(__name__)

RATE_PER_30S = 1
RATE_PER_HOUR = 5
WINDOW_SHORT = 30
WINDOW_LONG = 3600

MAX_MAIL_FILE = 12 * 1024 * 1024  # 12 MB для формы заявок

def _client_ip(request):
    ip = request.META.get('HTTP_X_REAL_IP')
    if ip: return ip.strip()
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff: return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')

def _rate_key(ip, kind): return f'reqs:{kind}:{ip}'

def _check_rate(ip):
    if settings.DEBUG:
        return True
    short_k = _rate_key(ip, '30s'); long_k = _rate_key(ip, '1h')
    short = cache.get(short_k, 0);   long  = cache.get(long_k, 0)
    if short >= RATE_PER_30S or long >= RATE_PER_HOUR: return False
    cache.add(short_k, 0, timeout=WINDOW_SHORT); cache.incr(short_k)
    cache.add(long_k, 0, timeout=WINDOW_LONG);  cache.incr(long_k)
    return True

def _recipients():
    emails = list(ReqsRecipient.objects.filter(is_active=True).values_list('email', flat=True))
    if emails:
        return emails
    return getattr(settings, 'REQS_EMAILS', None) or [getattr(settings, 'DEFAULT_FROM_EMAIL')]

def _send_async(message):
    try:
        message.send(fail_silently=False)
    except Exception:
        log.exception("Mail send failed")

@require_POST
def submit_request(request):
    ip = _client_ip(request)
    if not _check_rate(ip):
        return HttpResponseBadRequest('Too many requests.')

    # Ранний отсев по заголовку, чтобы не держать соединение зря
    cl = request.META.get('CONTENT_LENGTH')
    if cl:
        try:
            if int(cl) > MAX_MAIL_FILE:
                return HttpResponseBadRequest('File too large.')
        except ValueError:
            pass

    # Локально ограничиваем аплоад файла для этой вьюхи до 12 МБ
    request.upload_handlers = [
        MaxSizeUploadHandler(request, max_bytes=MAX_MAIL_FILE),
        MemoryFileUploadHandler(request),
        *request.upload_handlers,  # оставим прочие как fallback (TemporaryFileUploadHandler и т.д.)
    ]

    form = RequestForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest('Invalid data.')

    obj = form.save(commit=False)
    obj.save()

    site = get_current_site(request)
    ctx = {'obj': obj, 'when': timezone.localtime(obj.created_at), 'site': site.name}

    subject = f"Заявка с сайта {site.name}: {obj.name} — {obj.phone}"
    html = render_to_string('reqs/email_request.html', ctx)
    text = render_to_string('reqs/email_request.txt', ctx) or strip_tags(html)

    conn = get_connection(timeout=getattr(settings, 'EMAIL_TIMEOUT', 30))
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=_recipients(),
        headers={'Reply-To': obj.email} if obj.email else None,
        connection=conn,
    )
    msg.attach_alternative(html, "text/html")

    f = form.cleaned_data.get('file')
    if f:
        msg.attach(f.name, f.read(), getattr(f, 'content_type', 'application/octet-stream'))

    threading.Thread(target=_send_async, args=(msg,), daemon=True).start()
    back = request.META.get('HTTP_REFERER') or reverse('home')
    return redirect(back)
