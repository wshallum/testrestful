from django.test import TestCase
from django.db import IntegrityError
import json
try:
	import urlparse
except ImportError:
	import urllib.parse as urlparse
from .models import Entry, Phone

def load_json_from_bytestring(b):
    return json.loads(b.decode('utf-8'))


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
        load_json_from_bytestring(response.content)

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
        data = load_json_from_bytestring(response.content)
        self.assertEqual(data['name'], 'Joe')
        entry_url = urlparse.urlparse(data['url'])
        self.assertEqual(entry_url.path, location_url.path)

        # GET /entries search for new entry
        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        entries = load_json_from_bytestring(response.content)
        new_entry = None
        for entry in entries:
            if entry['url'] == data['url']:
                new_entry = entry
                break
        self.assertTrue(new_entry is not None)
        self.assertEquals(new_entry['url'], data['url'])
        self.assertEquals(new_entry['name'], 'Joe')

    def test_entries_post_to_create_with_phone(self):
        """Test POST /entries with phone works."""
        # POST /entries
        entry_data = dict(
            name='Joe',
            phones=[
                dict(type='home', number='123'),
                dict(type='mobile', number='456')])
        response = self.client.post(
            '/entries', data=json.dumps(entry_data),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        location = response['location']
        location_url = urlparse.urlparse(location)

        # GET new entry URL
        response = self.client.get(location_url.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = load_json_from_bytestring(response.content)
        self.assertEqual(data['name'], 'Joe')
        self.assertEqual(len(data['phones']), 2)
        for phone in data['phones']:
            if phone['type'] == 'home':
                self.assertEqual(phone['number'], '123')
            elif phone['type'] == 'mobile':
                self.assertEqual(phone['number'], '456')
            else:
                self.assertTrue(False, "unexpected phone type")
        entry_url = urlparse.urlparse(data['url'])
        self.assertEqual(entry_url.path, location_url.path)


class EntryUpdateTests(TestCase):
    def test_entry_put_to_update(self):
        # create
        response = self.client.post(
            '/entries',
            data=json.dumps(dict(name='Joe')), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        location = response['location']
        location_url = urlparse.urlparse(location)

        # update
        response = self.client.put(
            location_url.path,
            data=json.dumps(dict(name='Jane')),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # get again, should be changed
        response = self.client.get(location_url.path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = load_json_from_bytestring(response.content)
        self.assertEqual(data['name'], 'Jane')


class PhoneTests(TestCase):

    def test_create_and_get_phone(self):
        """Test creating Phone"""
        entry = Entry.objects.create(name='Joe')
        number_1 = Phone.objects.create(
            type='mobile', number='0123', parent=entry)
        number_2 = Phone.objects.get(id=number_1.id)
        self.assertEquals(number_1.type, number_2.type)
        self.assertEquals(number_1.number, number_2.number)
        self.assertEquals(number_1.parent, number_2.parent)

    def test_deleting_parent_cascades_to_phones(self):
        """Test that phones are deleted when parent entry is deleted."""
        entry = Entry.objects.create(name='Joe')
        number = Phone.objects.create(
            type='mobile', number='0123', parent=entry)
        the_id = number.id
        entry.delete()
        with self.assertRaises(Phone.DoesNotExist):
            Phone.objects.get(id=the_id)

    def test_saving_fails_without_parent_entry(self):
        with self.assertRaises(IntegrityError):
            Phone.objects.create(type='mobile', number='0123')
