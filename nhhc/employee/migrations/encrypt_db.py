from django.contrib.postgres.operations import CryptoExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("employee", "0001_initial")]

    operations = [CryptoExtension()]
