import inspect
from contextlib import contextmanager

import pytest
from pytest_django.fixtures import SettingsWrapper

_transactions_stack = []


def finish_fixture(vprint, request, name):
    fixturemanager = request.session._fixturemanager
    defs = fixturemanager.getfixturedefs(name, request.node.nodeid)
    vprint('Finish variants: {}'.format(defs))
    if defs:
        for d in reversed(defs):
            d.finish(request)


@contextmanager
def atomic_rollback(vprint, name, fixturename, fixturemanager):
    from django.db import transaction

    sid = transaction.savepoint()
    _transactions_stack.append(fixturename)
    vprint('transaction start: {} {}'.format(name, sid))
    yield
    if _transactions_stack:
        curr = _transactions_stack[-1]
        while curr and curr != fixturename:
            finish_fixture(vprint, fixturemanager, curr)
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
        return atomic_rollback(vprint, formatted, fixturename, request)
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


try:
    from pytest_django.fixtures import django_assert_num_queries
except ImportError:
    @pytest.fixture(scope='function')
    def django_assert_num_queries(pytestconfig):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        @contextmanager
        def _assert_num_queries(num):
            with CaptureQueriesContext(connection) as context:
                yield
                if num != len(context):
                    msg = "Expected to perform %s queries but %s were done" % (num, len(context))
                    if pytestconfig.getoption('verbose') > 0:
                        sqls = (q['sql'] for q in context.captured_queries)
                        msg += '\n\nQueries:\n========\n\n%s' % '\n\n'.join(sqls)
                    else:
                        msg += " (add -v option to show queries)"
                    pytest.fail(msg)

        return _assert_num_queries
