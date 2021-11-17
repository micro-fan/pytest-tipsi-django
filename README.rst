pytest-tipsi-django
===================

.. image:: https://img.shields.io/github/workflow/status/micro-fan/pytest-tipsi-django/master
   :alt: GitHub Workflow Status
   :target: https://github.com/micro-fan/pytest-tipsi-django/actions

.. image:: https://img.shields.io/pypi/v/pytest-tipsi-django.svg
   :target: https://pypi.python.org/pypi/pytest-tipsi-django/


.. contents:: **Table of Contents**
    :backlinks: none


Installation
------------

.. code-block:: bash

    $ pip install pytest-tipsi-django
    
Features 
------------

Default django test settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  - if you run pytest after install pytest-tipsi-django, 
    Configuration already has django settings.CACHE['default']
   
  - of course if you has Custom django settings, this settings to below are ignored.

.. code-block:: python
    
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    BROKER_BACKEND = 'memory'
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 60 * 15
        }
    }

API helpers
^^^^^^^^^^^

There is built-in fixture ``anonymouse_client`` and you can create helpers for your users wrapping them with `pytest_tipsi_django.client_fixtures.UserWrapper`.


It provides you usefull helpers for all request types.

``expected`` parameter in ``<METHOD>_json`` is very usefull to prevent tedious status code checks.


.. code-block:: python

   from pytest_tipsi_django.client_fixtures import UserWrapper

   def test_00_anonymous(anonymous_client, some_url):
       query_params = {'filter': 'query'}
       body = {'param1': 'param''}

       anonymous_client.get_json(some_url, query_params, expected=401)
       anonymous_client.post_json(some_url, body, expected=403)

       json_response = anonymous_client.patch_json(some_url, body)
       anonymous_client.put_json(some_url, body)
       anonymous_client.delete_json(some_url)


   @pytest.fixture
   def user_client(user_object):
       yield UserWrapper(user_client)

   def test_01_authorized(user_client, some_url):
       resp_json = user_client.get_json(some_url, expected=200)
   
  
Other fixtures
^^^^^^^^^^^^^^

* ``debug_db_queries`` - prints performed queries
  

License
-------

pytest-tipsi-django is distributed under the terms of the
`MIT License <https://choosealicense.com/licenses/mit>`_.
