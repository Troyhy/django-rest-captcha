from django.core.cache import caches
from rest_framework import views, response

from .settings import api_settings
from .serializers import ImageSerializer

cache = caches[api_settings.CAPTCHA_CACHE]


class RestCaptchaView(views.APIView):
    serializer_class = ImageSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """get captcha image, solve it, then send solution and captcha key to any other endpoint,
        where captcha is required"""

        serializer = self.serializer_class()
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
