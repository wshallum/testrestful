import json
import requests
from base_be_test import BaseBackendTest


class TestAddAndGetEntries(BaseBackendTest):

    def test_add_and_get_entries(self):
        # First the user sees no entries when he looks at the list of all
        # entries
        all_entries = requests.get(self.url('/entries'))
        self.assertEqual(
            all_entries.status_code, 200, "GET /entries returns 200")
        self.assertEqual(
            all_entries.headers['content-type'], "application/json",
            "GET /entries content-type is JSON")
        # The user then adds an entry
        add_result = requests.post(
            self.url('/entries'), json.dumps(dict(name="Joe")))
        self.assertEqual(
            add_result.status_code, 201, "POST /entries to create returns 201")
        # The user checks that the entry is there when he lists all entries
        all_entries = requests.get(self.url('/entries'))
        self.assertIn("Joe", all_entries.content)
        self.assertEqual(all_entries.status_code, 200)
