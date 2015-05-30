import json
import requests
from base_be_test import BaseBackendTest


class TestAddAndGetEntries(BaseBackendTest):

    def test_add_and_get_entries(self):
        # First the user sees no entries when he looks at the list of all
        # entries
        all_entries = requests.get(self.url('/entries'))
        self.assertResponseCodeAndContentType(
            all_entries, 200, 'application/json',
            'GET /entries returns 200 application/json')
        # The user then adds an entry
        add_result = requests.post(
            self.url('/entries'), json.dumps(dict(name="Joe")),
            headers={'content-type': 'application/json'})
        self.assertResponseCodeAndContentType(
            add_result, 201, 'application/json',
            'POST /entries returns 201 application/json')
        new_entry_url = add_result.json()['url']
        # The user checks that the entry is there when he lists all entries
        all_entries = requests.get(self.url('/entries'))
        self.assertResponseCodeAndContentType(
            all_entries, 200, 'application/json',
            'GET /entries returns 200 application/json')
        new_entry = None
        for entry in all_entries.json():
            if entry['url'] == new_entry_url:
                new_entry = entry
                break
        self.assertTrue(new_entry is not None, 'new entry found')
        self.assertEqual(
            new_entry['name'], 'Joe', 'new entry has correct name')
        # The user tries to get the individual entry
        get_entry_result = requests.get(new_entry_url)
        self.assertResponseCodeAndContentType(
            get_entry_result, 200, 'application/json',
            'GET entry url returns 200 application/json')
        get_entry_json = get_entry_result.json()
        self.assertEquals(
            get_entry_json['url'], new_entry_url, 'Entry URL matches')
        self.assertEquals(get_entry_json['name'], 'Joe', 'Entry name matches')
