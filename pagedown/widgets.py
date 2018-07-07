from django import VERSION, forms
from django.contrib.admin import widgets as admin_widgets
from django.template import Context, loader
from django.utils.html import conditional_escape
from django.conf import settings
from django.forms.utils import flatatt

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


class PagedownWidget(forms.Textarea):

    def __init__(self, *args, **kwargs):
        self.show_preview = kwargs.pop(
            "show_preview", getattr(settings, "PAGEDOWN_SHOW_PREVIEW", True))
        self.template = kwargs.pop(
            "template", getattr(settings, "PAGEDOWN_WIDGET_TEMPLATE", "pagedown/widgets/default.html"))
        self.css = kwargs.pop("css", getattr(settings, "PAGEDOWN_WIDGET_CSS", ("pagedown/demo/browser/demo.css",)))
        super(PagedownWidget, self).__init__(*args, **kwargs)

    def _media(self):
        return forms.Media(
            css={
                "all": self.css
            },
            js=(
                "pagedown/Markdown.Converter.js",
                "pagedown-extra/pagedown/Markdown.Converter.js",
                "pagedown/Markdown.Sanitizer.js",
                "pagedown/Markdown.Editor.js",
                "pagedown-extra/Markdown.Extra.js",
                "pagedown_init.js",
            ))

    media = property(_media)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""

        final_attrs = self.build_attrs(attrs, {'name': name})
        final_attrs = self.build_attrs(final_attrs, self.attrs)

        if "class" not in final_attrs:
            final_attrs["class"] = ""
        final_attrs["class"] += " wmd-input"
        template = loader.get_template(self.template)

        context = {
            "attrs": flatatt(final_attrs),
            "body": conditional_escape(force_unicode(value)),
            "id": final_attrs["id"],
            "show_preview": self.show_preview,
        }
        context = Context(context) if VERSION < (1, 9) else context
        return template.render(context)


class AdminPagedownWidget(PagedownWidget, admin_widgets.AdminTextareaWidget):
    def _media(self):
        return super(AdminPagedownWidget, self).media + forms.Media(
            css={
                "all": "admin/css/pagedown.css",
            },
            js=(
                "admin/js/pagedown.js",
            ))

    media = property(_media)
