from datetime import date

from django import template

register = template.Library()


def calculateLengthOfEmployment(start, end):
    date(start)
