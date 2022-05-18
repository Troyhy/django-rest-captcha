from django.core.cache import caches
from rest_framework import views, response

from .settings import api_settings
from .serializers import ImageSerializer

cache = caches[api_settings.CAPTCHA_CACHE]


class RestCaptchaView(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        serializer = ImageSerializer()
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
