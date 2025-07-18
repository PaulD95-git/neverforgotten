from django.shortcuts import render


def index(request):
    """
    Render the index page of the memorial app.
    """
    return render(request, 'memorial/index.html')
