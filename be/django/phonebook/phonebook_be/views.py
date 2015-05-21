from django.http import HttpResponse


def entries(request):
    return HttpResponse('{}', content_type='application/json')
