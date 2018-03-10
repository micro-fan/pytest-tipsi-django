import pytest

from pytest_tipsi_django import client_fixtures
from pytest_tipsi_django.client_fixtures import UserWrapper
from pytest_tipsi_django.django_fixtures import (  # noqa
    session_settings, module_settings, function_settings,
    module_transaction, function_fixture, module_fixture,
    django_assert_num_queries
)


def setup_docs_logger(item):
    func = item.function
    if hasattr(func, 'docme') and item.config.getoption('write_docs'):
        client_fixtures.request_logger = client_fixtures.RequestLogger(item)
    elif item.config.getoption('verbose_request'):
        client_fixtures.request_logger = client_fixtures.RequestVerbose(item)


def pytest_addoption(parser):
    group = parser.getgroup('docme')
    group.addoption('--write-docs', action='store_true', default=False,
                    help='Write http requests for documentation')
    group.addoption('--verbose_request', action='store_true', default=False,
                    help='Print all requests to stdout')

def pytest_configure(config):
    options = ['write_docs', 'verbose_request']
    if all(config.getoption(opt) for opt in options):
        raise pytest.UsageError("Use only one option at the same time {}".format(options))


@pytest.fixture
def docs_logger():
    """
    Make requests without being logged:

    >>> def my_test(docs_logger):
    ...     with docs_logger.silent():
    ...        client.get_json(url)  # not logged
    ...     client.get_json(url)  # logged
    """
    yield client_fixtures.request_logger


def finish_docs_logger(item, nextitem):
    func = item.function
    if hasattr(func, 'docme'):
        client_fixtures.request_logger.finish()
        client_fixtures.request_logger = client_fixtures.RequestLoggerStub()


@pytest.fixture(autouse=True)  # noqa: F811
def auto_transaction(request):
    """
    It should be the last fixture, so we ensure that we've loaded all other required fixtures
    before open transaction.
    If we meet error here, try to modify `if` as `name not in (request.fixturename, OTHERNAME)`
    """
    if 'module_transaction' not in request.fixturenames:
        yield None
    else:
        # We cannot request module_transaction or it will be used for all our tests
        module_transaction = request.getfixturevalue('module_transaction')  # noqa: F811
        with module_transaction(request.fixturename):
            yield


@pytest.fixture(scope='session', autouse=True)  # noqa
def local_cache(session_settings, django_db_setup):
    session_settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    session_settings.BROKER_BACKEND = 'memory'
    session_settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 60 * 15
        }
    }
    yield session_settings


@pytest.fixture
def anonymous_client(module_transaction):
    yield UserWrapper(None)


def pytest_runtest_setup(item):
    setup_docs_logger(item)


def pytest_runtest_teardown(item, nextitem):
    finish_docs_logger(item, nextitem)
