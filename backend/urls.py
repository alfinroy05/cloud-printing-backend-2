from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

def redirect_to_api(request):
    return HttpResponseRedirect('/api/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_api),  # ✅ Redirects `/` to `/api/`
    path('api/', include('api.urls')),
  

]
