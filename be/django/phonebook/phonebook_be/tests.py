from django.test import TestCase
import json


class EntriesListTests(TestCase):

    def test_entries_list(self):
        """Test GET /entries returns 200 with JSON content."""
        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        json.loads(response.content)

    def test_entries_post_to_create(self):
        """Test POST /entries returns 201."""
        response = self.client.post(
            '/entries',
            data=json.dumps(dict(name='Joe')), content_type='application/json')
        self.assertEqual(response.status_code, 201)
