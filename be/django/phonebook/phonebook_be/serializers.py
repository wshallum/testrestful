from rest_framework import serializers
from .models import Entry


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='entry', lookup_field='id')

    class Meta:
        model = Entry
        fields = ('url', 'name')
