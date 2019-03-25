from io import open

from setuptools import find_packages, setup

with open('pytest_tipsi_django/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = [
    'django',
    'pytest>=3.3.0',
    'pytest-django==3.4.*',
    'tipsi-tools>=1.7.0',
    'pytest-tipsi-testing>=1.3.0',
]

setup(
    name='pytest-tipsi-django',
    version=version,
    description='',
    long_description=readme,
    author='cybergrind',
    author_email='cybergrind@gmail.com',
    maintainer='cybergrind',
    maintainer_email='cybergrind@gmail.com',
    url='https://github.com/tipsi/pytest-tipsi-django',
    license='MIT',

    entry_points={
        'pytest11': ['pytest_tipsi_django = pytest_tipsi_django.plugin'],
    },

    keywords=[
        'pytest', 'pytest-django', 'fixtures', 'transactions', 'scopes',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
