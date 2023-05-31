from pytest import fixture
from config import Config


def pytest_addoption(parser):
    parser.addoption('--pdf-path',
                     action='store',
                     help='Specify PDF file to test')


@fixture(scope="session")
def get_parameters(request):
    config_param = {
        'pdf-path': request.config.getoption('--pdf-path'),
    }
    return config_param


@fixture(scope="session")
def app_config(get_parameters):
    configuration = Config(get_parameters)
    return configuration
