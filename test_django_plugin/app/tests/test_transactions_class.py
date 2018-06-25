import pytest

from test_django_plugin.app.models import Author, Book


class TestFixturesInClass:
    @pytest.fixture(scope='module')
    def lem(self, module_transaction):
        with module_transaction('lem'):
            yield Author.objects.create(first_name='Stanislav', last_name='Lem')

    @pytest.fixture(scope='module')
    def fat(self, module_transaction):
        with module_transaction('fat'):
            yield Author.objects.create(first_name='Leo', last_name='Fat')

    @pytest.fixture(scope='module')
    def henry(self, module_transaction):
        with module_transaction('henry'):
            yield Author.objects.create(first_name='O', last_name='Henry')

    @pytest.fixture(scope='module')
    def solaris(self, lem, module_transaction):
        with module_transaction('solaris'):
            yield Book.objects.create(name='Solaris', year=1961, author=lem)

    def test_01(self):
        assert Book.objects.count() == 0

    def test_02(self, fat, lem):
        assert Book.objects.count() == 0
        assert Author.objects.count() == 2

    def test_03(self, fat, henry):
        assert Book.objects.count() == 0
        assert Author.objects.count() == 2

    def test_04(self, lem, henry):
        assert Book.objects.count() == 0
        assert Author.objects.count() == 2

    def test_10(self, solaris):
        assert Book.objects.count() == 1
        assert Author.objects.count() == 1

    def test_99(self):
        assert Book.objects.count() == 0
