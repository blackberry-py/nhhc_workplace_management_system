from django.conf import settings
from portal.models import FeatureFlag


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled, first checking dynamic settings."""
    if flag := FeatureFlag.objects.filter(name=feature_name).first():
        return flag.is_enabled
    # Fall back to static settings if not found in database
    return settings.FEATURE_FLAGS.get(feature_name, False)
