import django, os, sys, json
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with open('port.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', 'cases', indent=2, stdout=f)

