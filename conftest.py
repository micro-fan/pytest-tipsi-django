def pytest_addoption(parser):
    group = parser.getgroup('tipsi_group')
    group.addoption('--docker-skip', action='store_true', default=False,
                    help='skip docker initialization')
