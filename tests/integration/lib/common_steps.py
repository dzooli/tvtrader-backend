from pprint import pprint
import requests
from pytest_bdd import then, parsers, given, when

from .fixtures import base_url


@given("server available")
def step_server_running():
    assert True


@then(parsers.parse("response code is {code:n}"))
def check_status(response, code):
    assert response.status_code == code


@when(parsers.parse('GET "{endpoint}" route'), target_fixture="response")
def get_endpoint(endpoint, base_url):
    with requests.Session() as session:
        return session.get(f"{base_url}{endpoint}")


@then(parsers.parse('message contains "{checkstr}"'))
def check_content(checkstr, response):
    assert hasattr(response, "text") and checkstr in str(response.text)
