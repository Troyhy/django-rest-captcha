import uuid
import base64

from django.utils.translation import gettext as _
from django.core.cache import caches
from rest_framework import serializers

from .settings import api_settings
from . import utils
from . import captcha

cache = caches[api_settings.CAPTCHA_CACHE]


class RestCaptchaSerializer(serializers.Serializer):
    captcha_key = serializers.CharField(max_length=64, write_only=True)
    captcha_value = serializers.CharField(max_length=8, write_only=True, trim_whitespace=True)

    def validate(self, data):
        super(RestCaptchaSerializer, self).validate(data)
        cache_key = utils.get_cache_key(data["captcha_key"])

        if data["captcha_key"] in api_settings.MASTER_CAPTCHA:
            real_value = api_settings.MASTER_CAPTCHA[data["captcha_key"]]
        else:
            real_value = cache.get(cache_key)

        if real_value is None:
            raise serializers.ValidationError(_("Invalid or expired captcha key"))

        cache.delete(cache_key)
        if data["captcha_value"].upper() != real_value:
            raise serializers.ValidationError(_("Invalid captcha value"))

        del data["captcha_key"]
        del data["captcha_value"]
        return data


class ImageSerializer(serializers.Serializer):
    captcha_key = serializers.CharField(
        max_length=64, help_text="unique captcha id (uuid4)"
    )
    captcha_image = serializers.CharField(help_text="base64 encoded image")
    image_type = serializers.CharField(help_text="always will be image/png")
    image_decode = serializers.CharField(help_text="always will be base64")

    def __init__(self, **kwargs):
        key = str(uuid.uuid4())
        value = utils.random_char_challenge(api_settings.CAPTCHA_LENGTH)
        cache_key = utils.get_cache_key(key)
        cache.set(cache_key, value, api_settings.CAPTCHA_TIMEOUT)

        # generate image
        image_bytes = captcha.generate_image(value)
        image = base64.b64encode(image_bytes)
        super().__init__(
            data={
                "captcha_key": key,
                "captcha_image": image.decode("ascii"),
                "image_type": "image/png",
                "image_decode": "base64",
            },
            **kwargs
        )
        self.is_valid()
