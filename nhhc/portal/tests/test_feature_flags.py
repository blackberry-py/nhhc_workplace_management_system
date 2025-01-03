from django.conf import settings
from django.test import TestCase

from nhhc.models import FeatureFlag
from nhhc.utils.feature_flags import is_feature_enabled


class FeatureFlagTestCase(TestCase):
    def test_static_feature_flag(self):
        settings.FEATURE_FLAGS["test_feature"] = True
        self.assertTrue(is_feature_enabled("test_feature"))

    def test_dynamic_feature_flag(self):
        FeatureFlag.objects.create(name="dynamic_feature", is_enabled=True)
        self.assertTrue(is_feature_enabled("dynamic_feature"))
