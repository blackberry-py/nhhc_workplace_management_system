import os
import random
import re
import string

from django.template.defaultfilters import slugify as slugify_django
from django.utils.encoding import force_str
from django.utils.timezone import now


def create_random_filename():
    chars = string.ascii_lowercase + string.ascii_uppercase
    return "".join(random.choice(chars) for _ in range(10))


def get_valid_filename_django(name: str) -> str:
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    s = create_random_filename()
    if s in {"", ".", ".."}:
        raise SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    return s


def slugify(string: str) -> str:
    return slugify_django(force_str(string))


def get_valid_filename(s: str) -> str:
    """
    like the regular get_valid_filename, but also slugifies away
    umlauts and stuff.
    """
    s = get_valid_filename_django(s)
    filename, ext = os.path.splitext(s)
    filename = slugify(create_random_filename)
    ext = slugify(ext)
    if ext:
        return "{}.{}".format(filename, ext)
    else:
        return "{}".format(filename)


def process_filename(instance, filename):
    return os.path.join(get_valid_filename(filename))
