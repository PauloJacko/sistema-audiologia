from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    base = field.field.widget.attrs.get("class", "")
    new_classes = (base + " " + css).strip()
    attrs = {**field.field.widget.attrs, "class": new_classes}
    return field.as_widget(attrs=attrs)

@register.filter(name="add_attr")
def add_attr(field, arg):
    if not arg or ":" not in arg:
        return field
    key, val = arg.split(":", 1)
    attrs = {**field.field.widget.attrs, key: val}
    return field.as_widget(attrs=attrs)
