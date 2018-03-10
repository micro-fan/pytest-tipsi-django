
class TestSettings:
    def test_01(self, function_settings, session_settings):
        function_settings.CUSTOM_SETTINGS = 5
        from django.conf import settings as dj_settings
        assert dj_settings.CUSTOM_SETTINGS == 5
        assert dj_settings.BROKER_BACKEND == 'memory'

    def test_02(self):
        from django.conf import settings
        assert settings.BROKER_BACKEND == 'memory'
