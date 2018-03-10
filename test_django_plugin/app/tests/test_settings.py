import pytest

from pytest_django.fixtures import SettingsWrapper


@pytest.fixture(scope='function')
def function_settings(module_settings):
    wrapper = SettingsWrapper()
    yield wrapper
    wrapper.finalize()


class TestSettings:
    def test_01(self, function_settings):
        function_settings.CUSTOM_SETTINGS = 5
        from django.conf import settings as dj_settings
        assert dj_settings.CUSTOM_SETTINGS == 5
        assert dj_settings.BROKER_BACKEND == 'memory'

    def test_02(self):
        # If test_01 runs before test_02 it brakes test_02
        from django.conf import settings
        assert settings.BROKER_BACKEND == 'memory'
