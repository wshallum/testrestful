from rest_framework import serializers
from .models import Entry, Phone
import six


class MultiKeyHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    Like HyperlinkedIdentityField but supports more than one field to put in
    the URL.

    Uses `lookup_kwarg_to_field` dict mapping view kwargs to field names for
    lookup.
    """
    def __init__(self, view_name=None, **kwargs):
        self.lookup_kwarg_to_field = dict(
            kwargs.pop('lookup_kwarg_to_field', {'pk': 'pk'}))
        super(MultiKeyHyperlinkedIdentityField, self).__init__(
            view_name, **kwargs)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = dict()
        for kwarg, field in six.iteritems(self.lookup_kwarg_to_field):
            lookup_kwargs[field] = view_kwargs[kwarg]
        return self.get_queryset().get(**lookup_kwargs)

    def get_url(self, obj, view_name, request, format):
        if obj.pk is None:
            return None

        view_kwargs = dict()
        for kwarg, field in six.iteritems(self.lookup_kwarg_to_field):
            view_kwargs[kwarg] = getattr(obj, field)
        return self.reverse(
            view_name, kwargs=view_kwargs, request=request, format=format)


class PhoneListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):

        def url_of(p):
            return self.child.to_representation(p)['url']

        existing_instances = {url_of(p): p for p in instance}
        existing_submitted_instances = {item['submitted_url']: item
                                        for item in validated_data
                                        if 'submitted_url' in item}
        new_submitted_instances = [item for item in validated_data
                                   if 'submitted_url' not in item]
        urls_to_delete = existing_instances.viewkeys() - \
            existing_submitted_instances.viewkeys()
        objects_to_delete = [existing_instances[u] for u in urls_to_delete
                             if u in existing_instances]
        objects_to_update = [(existing_instances[u], p) for u, p
                             in six.iteritems(existing_submitted_instances)
                             if u in existing_instances]

        result = []

        for o in objects_to_delete:
            o.delete()

        for existing, data in objects_to_update:
            result.append(self.child.update(existing, data))

        for data in new_submitted_instances:
            data['parent'] = self.root.instance
            result.append(self.child.create(data))

        return result


class WriteOnlySynonymField(serializers.Field):

    def __init__(self, **kwargs):
        kwargs['default'] = serializers.empty
        kwargs['required'] = False
        kwargs['write_only'] = True
        self.synonym_for = kwargs.pop('synonym_for')
        super(WriteOnlySynonymField, self).__init__(**kwargs)

    def get_value(self, dictionary):
        return dictionary.get(self.synonym_for, serializers.empty)

    def to_internal_value(self, data):
        return data


class PhoneSerializer(serializers.ModelSerializer):
    url = MultiKeyHyperlinkedIdentityField(
        view_name='phone',
        lookup_kwarg_to_field={'id': 'id', 'entry_id': 'parent_id'})
    submitted_url = WriteOnlySynonymField(synonym_for='url')

    class Meta:
        model = Phone
        list_serializer_class = PhoneListSerializer
        fields = ('type', 'number', 'url', 'submitted_url')


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='entry', lookup_field='id')
    phones = PhoneSerializer(many=True, required=False)

    class Meta:
        model = Entry
        fields = ('url', 'name', 'phones')

    def update(self, instance, validated_data):
        # pop this first so super does not complain about writable nested
        # serializers. we will update phones ourselves.
        phone_data = validated_data.pop('phones', [])
        phones_field = self.fields['phones']

        instance = super(EntrySerializer, self).update(instance, validated_data)

        phones_field.update(instance.phones.all(), phone_data)

        return instance

    def create(self, validated_data):
        phone_data = validated_data.pop('phones', [])
        new_entry = Entry.objects.create(**validated_data)
        # TODO atomically do this
        for phone_validated_data in phone_data:
            Phone.objects.create(parent=new_entry, **phone_validated_data)
        return new_entry
