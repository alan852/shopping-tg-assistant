import re
import os
from datetime import datetime
from typing import Iterator, TypedDict

import requests
from jsonpath_ng import parse

from cal_unit_cost import cal_unit_cost
from env import ENV, DEFAULT


class Transaction(TypedDict):
    description: str
    date: datetime


url: str = 'https://{domain}/api/v1/search/transactions'
jsonpath_desc: str = '$.data[*].attributes.transactions[*]'
jsonpath_total_pages: str = '$.meta.pagination.total_pages'
required_fields: str = ['description', 'date']

domain: str = None
token: str = None
desc_regex: str = None


def config_env():
    global domain, token, desc_regex
    if domain is None:
        domain = os.environ.get(ENV.FIREFLY_III_DOMAIN)
    if token is None:
        token = os.environ.get(ENV.FIREFLY_III_TOKEN)
    if desc_regex is None:
        desc_regex = os.environ.get(ENV.FIREFLY_III_TRAN_DESC_REGEX)\
            .replace("{units}", os.environ.get(ENV.UNITS, DEFAULT.UNITS))


def retrieve_transactions(query: str, page: int = 1) -> Iterator[Transaction]:
    config_env()
    response = requests.get(
        url.format(domain=domain),
        params={'query': query, 'page': page},
        headers={'Authorization': f'Bearer {token}'}
    )
    filtered_transactions = [
        {
            key: datetime.strptime(_.value[key][:-3] + _.value[key][-2:], '%Y-%m-%dT%H:%M:%S%z')
            if key == 'date' else _.value[key] for key in required_fields
        }
        for _ in parse(jsonpath_desc).find(response.json())
    ]
    yield from filtered_transactions
    if page != parse(jsonpath_total_pages).find(response.json())[0].value:
        yield from retrieve_transactions(query, page=page + 1)


cnv = {
    'G': {'factor': 1.0 / 1000.0, 'to': 'KG'},
    'ML': {'factor': 1.0 / 1000.0, 'to': 'L'}
}


def digest_transaction(transaction: Transaction):
    regex = rf'{desc_regex}'
    match = re.search(regex, transaction['description'], re.IGNORECASE)
    item = {'name': match.group('name'), 'size': float(match.group('size')),
            'unit': match.group('unit').upper(), 'cost': float(match.group('cost')),
            'store': match.group('store'), 'date': transaction['date']}
    item['unit_cost'] = cal_unit_cost(item['cost'], item['size'], item['unit'])
    return item
