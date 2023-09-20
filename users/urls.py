from django.urls import path, include

from users.views import RegisterView, ProfileUpdateView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('<int:pk>/', ProfileUpdateView.as_view(), name='user_profile_update'),
    path('register/', RegisterView.as_view(), name='register'),
    path('social-auth/', include('social_django.urls', namespace='social')),
]
