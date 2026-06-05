#!/usr/bin/env python
"""Utilitas command-line Django untuk proyek SSIS."""
import os
import sys


def main():
    """Menjalankan perintah manajemen Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
