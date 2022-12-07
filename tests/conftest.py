import typing as t

import pytest


# Pytest session fixtures---------------------------------------------------------------
def pytest_sessionstart(session: pytest.Session) -> None:
    """Called after the ``Session`` object has been created and before performing
    collection and entering the run test loop.

    Parameters
    ----------
    session
        The pytest session object.
    """


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Called after whole test run finished, right before returning the exit status
    to the system.

    Parameters
    ----------
    session
        The pytest session object.
    """


def pytest_addoption(parser: pytest.Parser) -> None:
    """Called to allow custom command line options to be added to pytest.

    Called once at the beginning of a test run.
    """
    # --all option skips any other options
    parser.addoption(
        "--all",
        action="store_true",
        dest="ALL",
        help="Skip all other options and run all tests.",
    )
    # --modifies option only runs tests marked with @pytest.mark.modifies
    parser.addoption(
        "--modifies",
        action="store_true",
        dest="MODIFIES",
        help="run tests marked with @pytest.mark.modifies",
    )
    # --slow option only runs tests marked with @pytest.mark.[minutes, hours, days]
    parser.addoption(
        "--slow",
        action="store_true",
        dest="SLOW",
        help="run tests marked with @pytest.mark.[minutes, hours, days]",
    )


def run_tests_with_mark_only_if_option(
    item: pytest.Item, mark_name: str, option_name: str
) -> None:
    """Run tests with the given mark name only if the given option name is set.

    Parameters
    ----------
    item
        The pytest item object.
    mark_name
        The name of the mark to check for.
    option_name
        The name of the command line option to check for.
    """
    # If mark is present and option is not present, skip test
    if mark_name in item.keywords and not item.config.getoption(option_name, None):
        pytest.skip(f"need {option_name} option to run {mark_name} mark")
    # If option is present and mark is not present, skip test
    if item.config.getoption(option_name, None) and mark_name not in item.keywords:
        pytest.skip(f"need {mark_name} mark to run {option_name} option")


def ensure_markers_not_combined(item: pytest.Item, mark_names: t.Sequence[str]) -> None:
    """Ensure that the given marks are not combined.

    Parameters
    ----------
    item
        The pytest item object.
    mark_names
        The names of the marks to check for.
    """
    marks = [mark for mark in mark_names if mark in item.keywords]
    assert len(marks) <= 1, f"cannot combine {marks}"


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Called to perform the setup phase.

    Here are the rules:
    --all: Run all tests
    --modifies: Runs tests marked with @pytest.mark.modifies
    --slow: Runs tests marked with @pytest.mark.[minutes, hours, days]

    See pyproject.toml for the purpose of each mark.
    """
    # If --all is set, run all tests
    if item.config.getoption("--all", None):
        # Do not process any other options
        return
    ensure_markers_not_combined(item, ("modifies", "slow"))
    run_tests_with_mark_only_if_option(item, "modifies", "--modifies")
    for mark in ("minutes", "hours", "days"):
        run_tests_with_mark_only_if_option(item, mark, "--slow")


# End of pytest session fixtures--------------------------------------------------------
