import json
import requests
from .base_be_test import BaseBackendTest


class TestUpdateEntries(BaseBackendTest):

    def test_add_and_update_entry_name(self):
        # The user adds an entry
        add_result = requests.post(
            self.url('/entries'), json.dumps(dict(name="Joe")),
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            add_result, 201, 'application/json',
            'POST /entries returns 201 application/json')
        new_entry_url = add_result.json()['url']

        # The user tries to get the individual entry
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        get_entry_json = get_entry_result.json()
        self.assertEquals(
            get_entry_json['url'], new_entry_url, 'Entry URL matches')
        self.assertEquals(get_entry_json['name'], 'Joe', 'Entry name matches')
        # The user updates the entry
        put_entry_result = requests.put(
            new_entry_url,
            data=json.dumps(dict(name='Ken')),
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            put_entry_result, 200, 'application/json',
            'PUT entry url returns 200 application/json')

        # The user tries to get the individual entry again
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        get_entry_json = get_entry_result.json()
        self.assertEquals(get_entry_json['name'], 'Ken', 'Entry name matches')

    def test_update_overwrites_phones(self):
        add_result = requests.post(
            self.url('/entries'),
            json.dumps(dict(
                name="Alice",
                phones=[
                    {'type': 'home', 'number': '0123'},
                    {'type': 'mobile', 'number': '0456'}
                ]
            )),
            headers={'content-type': 'application/json'})
        new_entry_url = add_result.json()['url']

        # The user updates the entry
        put_entry_result = requests.put(
            new_entry_url,
            data=json.dumps(dict(name='Ken', phones=[])),
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            put_entry_result, 200, 'application/json',
            'PUT entry url returns 200 application/json')

        # The user tries to get the individual entry again
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        get_entry_json = get_entry_result.json()
        self.assertEquals(get_entry_json['name'], 'Ken', 'Entry name matches')
        self.assertEquals(get_entry_json['phones'], [])
