from django.urls import path
from . import views

urlpatterns = [
    path('api/readers/', views.ReaderListCreateAPIView.as_view()),
    path('api/readers/<int:pk>/', views.ReaderRetrieveUpdateDestroyAPIView.as_view())
]
