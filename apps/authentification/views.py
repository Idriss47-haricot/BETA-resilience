from django.shortcuts import render

# Create your views here.


def configurer(request):
    return render(request, 'authentification/configurer.html')