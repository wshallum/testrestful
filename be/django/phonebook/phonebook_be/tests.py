from django.test import TestCase
import json


class EntriesListTests(TestCase):

    def test_entries_list(self):
        """Test GET /entries returns 200 with JSON content."""
        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        json.loads(response.content)
