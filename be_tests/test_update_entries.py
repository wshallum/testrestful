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

    def test_update_no_phones_deletes_phones(self):
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
            data=json.dumps(dict(
                name='Ken',
                phones=[{'type': 'office', 'number': '0789'}]
            )),
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            put_entry_result, 200, 'application/json',
            'PUT entry url returns 200 application/json')

        # The user tries to get the individual entry again
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        entry_json = get_entry_result.json()
        self.assertEquals(entry_json['name'], 'Ken', 'Entry name matches')
        self.assertEquals(len(entry_json['phones']), 1, 'Phone count matches')
        self.assertEquals(entry_json['phones'][0]['type'], 'office')
        self.assertEquals(entry_json['phones'][0]['number'], '0789')

    def test_update_can_add_phones(self):
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
        new_entry_json = add_result.json()
        new_entry_url = new_entry_json['url']

        new_entry_json['phones'].append({'type': 'office', 'number': '0789'})

        # The user updates the entry
        put_entry_result = requests.put(
            new_entry_url,
            json=new_entry_json,
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            put_entry_result, 200, 'application/json',
            'PUT entry url returns 200 application/json')

        # The user tries to get the individual entry again
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        entry_json = get_entry_result.json()
        self.assertEquals(len(entry_json['phones']), 3, 'Phone count matches')

    def test_resubmit_phones(self):
        self.maxDiff = None
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
        new_entry_data = add_result.json()
        new_entry_url = new_entry_data['url']
        self.assertEquals(
            len(new_entry_data['phones']), 
            2, 'Phone count matches')

        # The user resubmits the data again
        put_entry_result = requests.put(
            new_entry_url,
            data=add_result.text,
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            put_entry_result, 200, 'application/json',
            'PUT entry url returns 200 application/json')

        # The user tries to get the individual entry again and confirms 
        # it is equal
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        get_entry_json = get_entry_result.json()
        self.assertEquals(get_entry_json, new_entry_data)
