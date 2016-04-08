#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "executor.settings")
    os.environ.setdefault("NO_PROXY", "10.*.*.*,localhost,127.0.0.1")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
