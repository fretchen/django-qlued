""""
The tests for the module. This is the main test runner for the project. It can be executed as

`poetry run runtests`

It takes the argument of the tests that should be run. Take as an example that you would
like to run the the test_api_v2 only then you should execute

`poetry run python runtests.py tests.test_api_v2`


"""

import os

import click
import django
from django.conf import settings
from django.test.utils import get_runner


@click.command()
@click.option(
    "--names",
    help="The names of the tests that you would like to run.",
    default="tests",
)
def run_test(names: str):
    """
    Run the test suite for the project. It takes the argument of the tests that should be run.
    Take as an example that you would like to run the the test_api_v2 only then you should execute

    `poetry run runtests --names tests.test_api_v2`
    """
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
    django.setup()
    click.secho(f"Running tests for {names}", fg="green")
    t_runner_obj = get_runner(settings)
    test_runner = t_runner_obj()
    failures = test_runner.run_tests([names])
    click.secho(f"Tests failed: {failures}", fg="red" if failures else "green")
