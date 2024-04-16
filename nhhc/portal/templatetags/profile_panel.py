from typing import Dict, Optional, Union

from compliance.models import Compliance
from django import template
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.utils.html import escape, format_html
from django.utils.safestring import SafeText, mark_safe
from employee.models import Employee
