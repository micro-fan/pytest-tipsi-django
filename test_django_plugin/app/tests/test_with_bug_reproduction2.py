from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext


# issue: module fixture must exist,
# if not , these case raise  django.db.utils.OperationalError: (1305, 'SAVEPOINT s4737629504_x65 does not exist')
# remove below module fixture  it should be fail
# @pytest.fixture(scope='module', autouse=True)
# def this_is_module_fixture(module_fixture):
#     pass


@pytest.fixture(scope='function', autouse=False)
def this_is_function_fixture():
    return User.objects.create(username='this user available in function level')


@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist(request, http_client):
    #    assert User.objects.all().first().username == 'this user available in module level'
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist2():
    User.objects.create(username='this user available only in this testcase')

    assert 'this user available only in this testcase' in User.objects.all().values_list('username', flat=True)
    assert User.objects.count() == 1


@pytest.mark.usefixtures('this_is_function_fixture')
@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist3(http_client):
    assert 'this user available in function level' in User.objects.all().values_list('username', flat=True)
    assert User.objects.count() == 2


@pytest.mark.parametrize(
    argnames='parametrize_idx_aaa',
    argvalues=(1, 2, 3, 4,)
)
@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist4(parametrize_idx_aaa):
    User.objects.create(username=f'username_{parametrize_idx_aaa}')

    # assert 'this user available in module level' in User.objects.all().values_list('username', flat=True)
    assert f'username_{parametrize_idx_aaa}' in User.objects.all().values_list('username', flat=True)
    assert User.objects.count() == 1


@pytest.mark.parametrize(
    argnames='parametrize_idx_aaa,expected_value',
    argvalues=((1, 1), (2, 1), (3, 1), (4, datetime(2019, 10, 11)),)
)
@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist401(request, http_client, parametrize_idx_aaa, expected_value):
    print(f'\n\n\n--여기여기---{request.fixturenames}----------\n\n\n')

    User.objects.create(username=f'username_{parametrize_idx_aaa}')

    assert f'username_{parametrize_idx_aaa}' in User.objects.all().values_list('username', flat=True)
    assert User.objects.count() == 2


@pytest.mark.parametrize(
    argnames='parametrize_idx_aaa,expected_value',
    argvalues=((1, 1), (2, 1), (3, 1), (4, datetime(2019, 10, 11)),)
)
@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist402(http_client, parametrize_idx_aaa, expected_value):
    User.objects.create(username=f'username_{parametrize_idx_aaa}')

    assert f'username_{parametrize_idx_aaa}' in User.objects.all().values_list('username', flat=True)
    assert User.objects.count() == 2



@pytest.mark.parametrize(
    argnames='parametrize_idx_aaa,expected_value',
    argvalues=((1, ValueError), (2,ValueError), (3, ValueError), (4, ValueError),)
)
@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist402(http_client, parametrize_idx_aaa, expected_value):
    User.objects.create(username=f'username_{parametrize_idx_aaa}')
    try:
        raise ValueError
    except ValueError:
        pass
    assert f'username_{parametrize_idx_aaa}' in User.objects.all().values_list('username', flat=True)
    assert User.objects.count() == 2


@pytest.mark.django_db
def test_check_raise_savepiont_does_not_exist5(http_client):
    from django.db import connection
    with CaptureQueriesContext(connection) as expected_num_queries:
        User.objects.create(username=f'username_123')

    with CaptureQueriesContext(connection) as expected_num_queries2:
        http_client.get(path='www.naver.com')

    assert len(expected_num_queries.captured_queries) == 1
    assert User.objects.count() == 2
