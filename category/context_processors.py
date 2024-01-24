from category.models import Category


def menu_links(request):
    categories = Category.objects.all()
    return dict(categories=categories)
