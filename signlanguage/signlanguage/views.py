from django.shortcuts import render
from django.http import HttpResponse

import sys
from subprocess import run, PIPE

def button(request):
    return render(request, 'signlanguage.html')



def external(request):
    inp=request.FILES.get('param')
    out = run(sys.executable,['//Users//anishasinghoberoi//django-webapp//signlanguage//signlanguage//download.py', inp], shell = False, stdout = PIPE)
   
    print(out)
    return render(request,'signlanguage.html', {'data1':out})