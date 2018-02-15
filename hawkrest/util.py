def get_auth_header(request):
    return request.META.get('HTTP_AUTHORIZATION', '')


def is_hawk_auth_request(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    return auth_header.startswith('Hawk ')