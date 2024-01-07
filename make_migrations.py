import os
import sys
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

    args = sys.argv + ["makemigrations", "qlued"]
    execute_from_command_line(args)
