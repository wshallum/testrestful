from django.test import TestCase
import json
import urlparse
from .models import Entry


class EntryTests(TestCase):

    def test_create_and_get_entry(self):
        """Test creating Entry"""
        entry = Entry.objects.create(name='Joe')
        entry2 = Entry.objects.get(id=entry.id)
        self.assertEquals(entry.name, entry2.name)


class EntriesListTests(TestCase):

    def test_entries_list(self):
        """Test GET /entries returns 200 with JSON content."""
        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        json.loads(response.content)

    def test_entries_post_to_create(self):
        """Test POST /entries returns 201 and returns Location of new entry."""
        # POST /entries
        response = self.client.post(
            '/entries',
            data=json.dumps(dict(name='Joe')), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        location = response['location']
        location_url = urlparse.urlparse(location)

        # GET new entry URL
        response = self.client.get(location_url.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Joe')
        entry_url = urlparse.urlparse(data['url'])
        self.assertEqual(entry_url.path, location_url.path)

        # GET /entries search for new entry
        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        entries = json.loads(response.content)
        new_entry = None
        for entry in entries:
            if entry['url'] == data['url']:
                new_entry = entry
                break
        self.assertTrue(new_entry is not None)
        self.assertEquals(new_entry['url'], data['url'])
        self.assertEquals(new_entry['name'], 'Joe')
