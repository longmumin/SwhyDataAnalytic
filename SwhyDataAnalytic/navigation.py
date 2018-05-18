from django.shortcuts import render


import logging
logger = logging.getLogger('SwhyDataAnalytic.Debug')

def loadnavigationPage(request):
    return render(request, 'navigationpage.html')
