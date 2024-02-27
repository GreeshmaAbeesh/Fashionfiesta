from .models import Category

def menu_links(request):     # here we are going to fetch all the categories from the database (add this function name to templates in settings )
    links = Category.objects.all()
    return dict(links=links)    # takes request as an argument and returns the dictionary of data as a context.here take all categories list and store them into links.