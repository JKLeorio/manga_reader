from django import template

register = template.Library()

@register.filter
def verbose_name(the_object, the_field):
    return the_object._meta.get_field(the_field).verbose_name

@register.filter
def cut_description(description):
    allowable_length = 150
    text = "....."
    print(not description)
    if not description:
        return text
    elif len(description.split()) < 2:
        if len(description) <= allowable_length:
            return description + text
        else:
            return description[:allowable_length] + text
    short_description = str()
    for word in description.split():
        if len(short_description) + len(word) >= allowable_length:
            return short_description + text
        short_description += f" {word}"
    return short_description + text

@register.filter
def get_pages_slice(pages, the_page):
    slice_length_a_b = 2
    for i, page in enumerate(pages):
        if page.pk == the_page.pk:
            if i + slice_length_a_b + 1 >= pages.count():
                return f"{i - (slice_length_a_b * 2 - (pages.count() - i - 1))}:"
            elif i - slice_length_a_b < 0:
                return f":{slice_length_a_b * 2 + 1}"
            else:
                return f"{i-2}:{i+3}"

@register.filter
def get_model_index(query, the_record):
    for i, record in enumerate(query):
        if record.pk == the_record.pk:
            return i+1