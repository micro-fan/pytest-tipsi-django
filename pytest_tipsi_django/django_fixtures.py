import inspect
from contextlib import contextmanager

import pytest
from pytest_django.fixtures import SettingsWrapper

_transactions_stack = []


def get_fixture(fixturemanager, name):
    return fixturemanager._arg2fixturedefs[name][0]


def finish_fixture(request, name):
    fixturemanager = request.session._fixturemanager
    get_fixture(fixturemanager, name).finish(request)


@contextmanager
def atomic_rollback(request, vprint, name, fixturename):
    from django.db import transaction

    sid = transaction.savepoint()
    _transactions_stack.append(fixturename)
    vprint('transaction start: {} {}'.format(name, sid))
    yield
    if _transactions_stack:
        curr = _transactions_stack[-1]
        while curr and curr != fixturename:
            finish_fixture(request, curr)
            if _transactions_stack:
                curr = _transactions_stack[-1]
            else:
                curr = None
        if curr == fixturename:
            vprint('rollback {} {}'.format(name, sid))
            _transactions_stack.pop()
            transaction.savepoint_rollback(sid)


def get_atomic_rollback(request, vprint):
    def _inner(fixturename, *args, **kwargs):
        f = inspect.currentframe().f_back.f_code
        name = '{} at {}:{}'.format(f.co_name, f.co_filename, f.co_firstlineno)
        if args or kwargs:
            formatted = '{} / {} {}'.format(name, args, kwargs)
        else:
            formatted = name
        return atomic_rollback(request, vprint, formatted, fixturename)
    return _inner


@pytest.fixture(scope='module')
def module_transaction(request, vprint, django_db_blocker, django_db_setup):
    from django.db import connection, transaction

    django_db_blocker.unblock()
    with transaction.atomic():
        sid = transaction.savepoint()
        yield get_atomic_rollback(request, vprint)
        transaction.savepoint_rollback(sid)
    connection.close()


@pytest.fixture
def function_fixture(request, module_transaction):
    with module_transaction(request.fixturename):
        yield


@pytest.fixture(scope='module')
def module_fixture(request, module_transaction):
    with module_transaction(request.fixturename):
        yield


@pytest.fixture(scope='session')
def session_settings():
    wrapper = SettingsWrapper()
    yield wrapper
    wrapper.finalize()


@pytest.fixture(scope='module')
def module_settings(session_settings):
    wrapper = SettingsWrapper()
    yield wrapper
    wrapper.finalize()
