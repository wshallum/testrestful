from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from .models import Entry
from .serializers import EntrySerializer


@csrf_exempt
def entries(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = EntrySerializer(data=data)
        if serializer.is_valid():
            new_entry = serializer.save()
            response = HttpResponse(
                serializer.data, content_type='application/json')
            response.status_code = 201  # created
            response['location'] = reverse(
                'entry', kwargs=dict(id=new_entry.id))
            return response
    else:
        return HttpResponse('{}', content_type='application/json')


def entry(request, id):
    entry = Entry.objects.get(id=id)
    serializer = EntrySerializer(entry)
    json_data = JSONRenderer().render(serializer.data)
    response = HttpResponse(json_data, content_type='application/json')
    response.status_code = 200
    return response
