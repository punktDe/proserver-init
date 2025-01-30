#!/usr/bin/env python3
import json
import yaml
import requests
from typing import List


class Inventory:
    inventory_url = None
    vars = None

    def __init__(self, inventory_url='https://inventory.punkt.app'):
        self.inventory_url = inventory_url
        self._load_vars()
        self._load_public_keys()

    def _load_vars(self) -> None:
        with requests.get(f'{self.inventory_url}/defaults/main.yaml', stream=True, timeout=30) as response:
            self.vars = yaml.safe_load(response.content)

    def _load_public_keys(self) -> None:
        for user, user_info in self.vars['punktde']['people'].items():
            user_info['public_keys'] = self._get_public_keys(user, user_info['email'])

    def _get_public_keys(self, user: str, email: str) -> List:
        response = requests.get(f'{self.inventory_url}/files/public_keys/{user}.pub', timeout=30)
        if response.status_code != 200:
            return []

        public_keys = []
        for public_key in response.content.decode().splitlines():
            public_key = public_key.strip()
            if not public_key or public_key.startswith('#'):
                continue
            public_key = public_key.split(' ', 2)
            public_key = f'{public_key[0]} {public_key[1]} {email}'
            public_keys.append(public_key)
            break

        return public_keys

    def inventory(self):
        return {
            'all': {
                'vars': self.vars,
            }
        }

    def __str__(self) -> str:
        return json.dumps(self.inventory())


if __name__ == '__main__':
    print(str(Inventory()))
