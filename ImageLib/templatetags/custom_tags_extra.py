from django import template

register = template.Library()


@register.filter
def verbose_name(the_object, the_field):
    return the_object._meta.get_field(the_field).verbose_name


@register.filter
def cut_description(description):
    allowable_length = 150
    text = "....."
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
                return f"{i - 2}:{i + 3}"


@register.filter
def get_model_index(query, the_record):
    for i, record in enumerate(query):
        if record.pk == the_record.pk:
            return i + 1


@register.filter
def has_attr(obj, attr):
    return hasattr(obj, attr)


@register.filter
def get(obj, key):
    # result = obj
    # for key in keys:
    #     result = result[key]
    # return result
    if type(key) == int:
        return obj[key - 1]
    return obj[key]


@register.filter
def get_item(obj, key):
    return obj.get(key, None)


@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr)


@register.simple_tag()
def set_get_parameter(request, parameter, value):
    new_path = request.path_info + '?'
    new_request_get = request.GET.copy()
    new_request_get.update({parameter: value})
    for get_parameter, parameter_value in new_request_get.items():
        new_path += f'{get_parameter}={parameter_value}&'
    new_path = new_path[:-1]
    return new_path
