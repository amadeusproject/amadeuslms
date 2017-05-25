from django import template

register = template.Library()

@register.inclusion_tag('pagination.html')
def pagination(request, paginator, page_obj):
    context = {
        'request': request,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    page_numbers = []

    if paginator.num_pages <= 6:
        page_numbers = paginator.page_range
    else:
        init = page_obj.number - 4
        end = page_obj.number + 2

        if init <= 0:
            init = 1

        if end > paginator.num_pages:
            end = paginator.num_pages + 1

        if (end - init) < 6:
            if init == 1 and end < paginator.num_pages:
                end += (6 - (end - init))
            elif init > 1 and end == paginator.num_pages + 1:
                init -= (6 - (end - init))

        for n in range(init, end):
            if n > 0 and n <= paginator.num_pages:
                page_numbers.append(n)

    context['page_numbers'] = page_numbers

    getvars = request.GET.copy()

    if 'page' in getvars:
        del getvars['page']
        
    if len(getvars) > 0:
        context['getvars'] = '&%s' % getvars.urlencode()

    return context