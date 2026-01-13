from django.shortcuts import render

def inp_home(request):
    return render(request, 'inp/inp_home.html')
