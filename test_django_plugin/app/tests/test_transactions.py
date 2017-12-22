import pytest

from test_django_plugin.app.models import Author, Book


@pytest.fixture(scope='module')
def lem(module_transaction):
    with module_transaction('lem'):
        yield Author.objects.create(first_name='Stanislav', last_name='Lem')


@pytest.fixture
def solaris(function_fixture, lem):
    yield Book.objects.create(name='Solaris', year=1961, author=lem)


def test_00():
    assert Author.objects.count() == 0
    assert Book.objects.count() == 0


author_id = None
book_id = None


def test_01(solaris, lem):
    global author_id, book_id
    assert Author.objects.count() == 1
    assert Book.objects.count() == 1
    author_id = id(lem)
    book_id = id(solaris)


def test_02(solaris, lem):
    assert id(lem) == author_id
    assert id(solaris) != book_id
    assert Author.objects.count() == 1
    assert Book.objects.count() == 1


def test_03():
    assert Author.objects.count() == 0
    assert Book.objects.count() == 0


def test_04(solaris, lem):
    assert Author.objects.count() == 1
    assert Book.objects.count() == 1


def test_05():
    assert Author.objects.count() == 0
    assert Book.objects.count() == 0


def test_06(solaris, lem):
    assert Author.objects.count() == 1
    assert Book.objects.count() == 1
