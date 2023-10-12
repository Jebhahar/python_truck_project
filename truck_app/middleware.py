# # middleware.py
#
# from django.http import HttpResponseForbidden
#
# class SecretKeyMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         secret_key = request.headers['SECRETKEY']
#
#         if not secret_key or secret_key != 'django-insecure-1v1d-o8_v7r2owlh!x2aqhujhljp!_k^=@01knx1u1yual8l!2':
#             return HttpResponseForbidden('Forbidden')
#
#         response = self.get_response(request)
#         return response
