from django.conf import settings
from django.core.paginator import Paginator


# Выносим пагинатор отдельно, чтобы не повторяться
def paginate_page(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
