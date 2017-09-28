import os
import time
from contextlib import suppress
import pytest
from tipsi_tools.unix import wait_socket


def pytest_configure(config):
    if config.getoption('docker_skip'):
        return

    with suppress(Exception):
        print('Stop old container if exists')
        os.system('docker stop testpostgres')
        time.sleep(1)
    try:
        print('Start docker')
        os.system('docker run -d -p 40001:5432 --name=testpostgres --rm=true postgres')
        time.sleep(15)
        wait_socket('localhost', 40001, timeout=15)
        print('Create database')
        os.system('echo create database plugin | psql -h localhost -p 40001 -U postgres')
    except Exception as e:
        print('EXCEPTION: {}'.format(e))
        exit(1)


def pytest_unconfigure(config):
    if config.getoption('docker_skip'):
        return

    os.system('docker stop -t 2 testpostgres')


@pytest.fixture(autouse=True)
def autodatabase(module_transaction):
    pass
