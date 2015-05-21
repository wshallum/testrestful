from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def entries(request):
    if request.method == 'POST':
        response = HttpResponse('{}', content_type='application/json')
        response.status_code = 201  # created
        return response
    else:
        return HttpResponse('{}', content_type='application/json')
