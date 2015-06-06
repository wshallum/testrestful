from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from .models import Entry, Phone
from .serializers import EntrySerializer, PhoneSerializer


@csrf_exempt
def entries(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = EntrySerializer(data=data, context=dict(request=request))
        if serializer.is_valid(raise_exception=True):
            new_entry = serializer.save()
            json_data = JSONRenderer().render(serializer.data)
            response = HttpResponse(
                json_data, content_type='application/json')
            response.status_code = 201  # created
            response['location'] = reverse(
                'entry', kwargs=dict(id=new_entry.id))
            return response
    else:
        serializer = EntrySerializer(
            Entry.objects.all(), many=True, context=dict(request=request))
        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, content_type='application/json')


def entry(request, id):
    entry = Entry.objects.get(id=id)
    serializer = EntrySerializer(entry, context=dict(request=request))
    json_data = JSONRenderer().render(serializer.data)
    response = HttpResponse(json_data, content_type='application/json')
    response.status_code = 200
    return response


def phone(request, entry_id, id):
    phone = get_object_or_404(Phone, id=id, entry_id=entry_id)
    serializer = PhoneSerializer(phone, context=dict(request=request))
    json_data = JSONRenderer().render(serializer.data)
    response = HttpResponse(json_data, content_type='application/json')
    response.status_code = 200
    return response
