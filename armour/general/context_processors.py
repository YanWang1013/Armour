from django.conf import settings

def general(request):
    return {'REGISTARTION_VIEW': settings.REGISTARTION_VIEW, 'BLOCK_SOURCE': settings.BLOCK_SOURCE}
