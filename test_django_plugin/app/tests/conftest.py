import os
import time
from contextlib import suppress
import pytest
from tipsi_tools.unix import wait_socket, succ


def create_database():
    print('Create database')
    c = 0
    while c < 30:
        try:
            succ('echo create database plugin | psql -h localhost -p 40001 -U postgres')
            return
        except:
            c += 1
            time.sleep(1)


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
        time.sleep(5)
        wait_socket('localhost', 40001, timeout=15)
        create_database()
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
