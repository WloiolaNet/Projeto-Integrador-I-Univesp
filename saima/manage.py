#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # A linha abaixo define o caminho para o módulo de configurações do Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saima.settings')  # Verifique se 'saima.settings' é o caminho correto
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
