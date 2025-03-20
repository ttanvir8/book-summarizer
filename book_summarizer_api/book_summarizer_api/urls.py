"""
URL configuration for book_summarizer_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# book_summarizer_api/book_summarizer_api/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView
from django.http import JsonResponse, HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Add this custom callback view function
@api_view(['GET'])
def auth_callback(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the authentication token for this user
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=request.user)
        
        # Redirect to frontend with token in query params
        # This way the frontend can grab the token directly without additional API calls
        frontend_url = 'http://localhost:3000/auth/callback'
        redirect_url = f'{frontend_url}?token={token.key}'
        return HttpResponseRedirect(redirect_url)
        
    # If not authenticated, return error
    return Response({'detail': 'Authentication failed'}, status=401)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('booksummary.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
    # Then add these to your urlpatterns
path('auth/callback/', auth_callback, name='auth_callback'),
# You may also want to add a redirect from the Google callback to your callback
path('accounts/google/login/callback/', RedirectView.as_view(url='/auth/callback/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Add this line

if settings.DEBUG: # Only serve media in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)