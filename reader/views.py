from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Reader
from .serializers import ReaderSerializer


class ReaderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer
    permission_classes = [IsAuthenticated]


class ReaderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer
    permission_classes = [IsAuthenticated]
