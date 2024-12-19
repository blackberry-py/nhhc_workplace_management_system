from .settings import *  # Import your main settings

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": "testing_carenett_prod",
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": "blackberry-py-multi-tenet-prod-do-user-16979650-0.k.db.ondigitalocean.com",
        "PORT": 25060,
        "OPTIONS": {
            "sslmode": "require",
            "sslrootcert": os.environ["DB_CERT_PATH"],
        },
    }
}
