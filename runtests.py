#!/usr/bin/env python
""""
The tests for the module. This is the main test runner for the project. It can be executed as

`poetry run python runtests.py`

It takes the argument of the tests that should be run. Take as an example that you would
like to run the the test_api_v2 only then you should execute

`poetry run python runtests.py tests.test_api_v2`


"""
import os
import sys
import argparse

import django
from django.conf import settings
from django.test.utils import get_runner
from icecream import ic

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
django.setup()

parser = argparse.ArgumentParser(description="Run Django tests.")
parser.add_argument("tests", nargs="*", default=["tests"], help="The tests to be run.")
args = parser.parse_args()

ic(args.tests)
TestRunner = get_runner(settings)
test_runner = TestRunner()
failures = test_runner.run_tests(args.tests)
sys.exit(bool(failures))
