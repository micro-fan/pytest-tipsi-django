import pytest


@pytest.fixture
def invalid_fixture(module_transaction):
    with module_transaction('invalid_fixture'):
        raise Exception('FUFIX')


@pytest.mark.xfail
def test_invalid_fixture(invalid_fixture):
    pass
