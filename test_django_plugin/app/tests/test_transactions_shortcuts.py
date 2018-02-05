import pytest

from pytest_tipsi_django.django_fixtures import module_fx, function_fx


from test_django_plugin.app.models import Author, Book


@module_fx
def lem():
    return Author.objects.create(first_name='Stanislav', last_name='Lem')


@function_fx
def solaris(lem):
    return Book.objects.create(name='Solaris', year=1961, author=lem)


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


def test_04(solaris):
    assert Author.objects.count() == 1
    assert Book.objects.count() == 1
