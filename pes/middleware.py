# from django.http import JsonResponse
# from django.conf import settings
# from django.utils.deprecation import MiddlewareMixin

# class SlashMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         if not settings.APPEND_SLASH:
#             return None
        
#         if not request.path.endswith('/'):
#             return JsonResponse({'error': 'You are missing the slash at the end of the URL.'}, status=400)

#         return None


