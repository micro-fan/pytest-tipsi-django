pytest-tipsi-django
===================

.. image:: https://travis-ci.org/tipsi/pytest-tipsi-django.svg?branch=master
   :target: https://travis-ci.org/tipsi/pytest-tipsi-django
.. image:: https://img.shields.io/pypi/v/pytest-tipsi-django.svg
   :target: https://pypi.python.org/pypi/pytest-tipsi-django


.. contents:: **Table of Contents**
    :backlinks: none


Installation
------------

.. code-block:: bash

    $ pip install pytest-tipsi-django
    
Features 
------------

* Default django test settings

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
   
  
  
  
  

License
-------

pytest-tipsi-django is distributed under the terms of the
`MIT License <https://choosealicense.com/licenses/mit>`_.
