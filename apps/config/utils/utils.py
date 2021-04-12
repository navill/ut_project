import re
import sys
from urllib import parse

from django.db.models import F
from django.db.models.functions import Concat
from django.utils.timezone import now


def concatenate_name(target_field: str = None) -> Concat:
    first_name = 'first_name'
    last_name = 'last_name'
    if target_field:
        first_name = f'{target_field}__{first_name}'
        last_name = f'{target_field}__{last_name}'
    full_name = Concat(F(last_name), F(first_name))
    return full_name


def log_request(sender, environ, **kwargs):  # HTTP_USER_AGENT, HTTP_HOST, REMOTE_ADDR
    if "pytest" not in sys.modules:
        current_time = now().strftime("%Y-%m-%dT%H:%M:%S")
        method = environ['REQUEST_METHOD']
        host = environ['HTTP_HOST']
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']
        client_ip = environ['REMOTE_ADDR']
        client_agent = environ['HTTP_USER_AGENT']
        query = '?' + parse.unquote(query) if query else ''
        print(f'[{current_time}][{method}] {host}{path}{query} | IP_addr:{client_ip} | Agent: {client_agent}')


def convert_camel_case_to_snake(camel_str: str) -> str:
    splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', camel_str)).split()
    return '_'.join(splitted).lower() + 's'
