from django.http import HttpResponse
from django.shortcuts import render


def place_order(request):
    return HttpResponse("Place Order")
