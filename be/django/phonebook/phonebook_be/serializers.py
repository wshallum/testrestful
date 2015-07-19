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


class PhoneSerializer(serializers.HyperlinkedModelSerializer):
    url = MultiKeyHyperlinkedIdentityField(
        view_name='phone',
        lookup_kwarg_to_field={'id': 'id', 'entry_id': 'parent_id'})

    class Meta:
        model = Phone
        fields = ('type', 'number', 'url')


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='entry', lookup_field='id')
    phones = PhoneSerializer(many=True, required=False)

    class Meta:
        model = Entry
        fields = ('url', 'name', 'phones')

    def create(self, validated_data):
        phone_data = validated_data.pop('phones', [])
        new_entry = Entry.objects.create(**validated_data)
        # TODO atomically do this
        for phone_validated_data in phone_data:
            Phone.objects.create(parent=new_entry, **phone_validated_data)
        return new_entry
