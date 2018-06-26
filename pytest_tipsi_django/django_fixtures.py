import inspect
from contextlib import contextmanager

import pytest
from _pytest import fixtures
from pytest_django.fixtures import SettingsWrapper as OriginalSettingsWrapper

_transactions_stack = []


def get_defs_by_name(vprint, request, name):
    fixturemanager = request.session._fixturemanager
    defs = fixturemanager.getfixturedefs(name, request.node.nodeid)
    # see test_transaction_class.py to find failed case
    # class fixtures have baseid = <module>::<Class>::()
    # but tests have nodeid = <module>
    # so class fixtures basically have more precise scope than function
    # thus we need to wider scope for such cases
    if not defs and name in fixturemanager._arg2fixturedefs:
        defs = fixturemanager._arg2fixturedefs[name]
        vprint(
            'Get fixtures without respecting factories: {} {}'.format(request.node.nodeid, defs),
            level=2)

    # We need this only to finish fixtures in _transactions_stack
    # if we have no defs here - there will be infinite loop in atomic_rollback:while below
    assert defs, 'Cannot find: {} Available: {}'.format(
        name, list(fixturemanager._arg2fixturedefs.keys()))
    vprint('Finish variants: {} For: {}'.format(defs, name), level=3)
    return defs


def finish_fixture(vprint, request, name):
    defs = get_defs_by_name(vprint, request, name)
    if defs:
        for d in reversed(defs):
            d.finish(request)


@contextmanager
def atomic_rollback(vprint, name, fixturename, fixturemanager):
    from django.db import transaction

    sid = transaction.savepoint()
    try:
        _transactions_stack.append(fixturename)
        vprint('transaction start: {} {}'.format(name, sid), level=2)
        yield
    except Exception:
        fname = _transactions_stack.pop()
        assert fname == fixturename
        raise
    else:
        if _transactions_stack:
            curr = _transactions_stack[-1]
            while curr and curr != fixturename:
                vprint('Stack: {} {}'.format(_transactions_stack, curr))
                finish_fixture(vprint, fixturemanager, curr)
                if _transactions_stack:
                    curr = _transactions_stack[-1]
                else:
                    curr = None
            if curr == fixturename:
                vprint('rollback {} {}'.format(name, sid), level=2)
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


class SettingsWrapper(OriginalSettingsWrapper):
    """
    we need `_to_restore` to be object local to work with nesting
    see test_settings.py for test case
    """

    def __init__(self):
        self.__dict__['_to_restore'] = []
        assert id(SettingsWrapper._to_restore) != id(self._to_restore)


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


@pytest.fixture(scope='function')
def function_settings(module_settings):
    wrapper = SettingsWrapper()
    yield wrapper
    wrapper.finalize()


def transaction_fx(scope):
    """
    Shortcut for fixtures which uses module_transaction
    >>>@pytest.fixture(scope='module')
    ...def some_fx(request, sub_fx, module_transaction):
    ...    with module_transaction(request.fixturename):
    ...        yield SomeModel.objects.create(sub=sub_fx)
    vs
    >>>@module_fx
    ...def some_fx(sub_fx):
    ...    return SomeModel.objects.create(sub=sub_fx)
    """

    def _decorator(func):
        arg_names = fixtures.getfuncargnames(func)

        def _inner(request):
            requested_fixtures = [request.getfixturevalue(n) for n in arg_names]
            module_transaction = request.getfixturevalue('module_transaction')
            with module_transaction(request.fixturename):
                yield func(*requested_fixtures)

        return pytest.fixture(scope=scope, name=func.__name__)(_inner)

    return _decorator


module_fx = transaction_fx('module')
function_fx = transaction_fx('function')

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
