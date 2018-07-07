from django import forms
from .widgets import AdminPagedownWidget, PagedownWidget


class PagedownField(forms.CharField):
    widget = PagedownWidget


class AdminPagedownField(forms.CharField):
    widget = AdminPagedownWidget


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^pagedown\.forms\.PagedownField"])
    add_introspection_rules([], ["^pagedown\.forms\.AdminPagedownField"])
except ImportError:
    raise
