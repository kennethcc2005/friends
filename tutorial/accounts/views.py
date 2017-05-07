# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer
from rest_framework import generics, status
from django.contrib.auth.models import User
from accounts.serializers import UserSerializer
from rest_framework import permissions
from travel_with_friends.permissions import IsOwnerOrReadOnly, IsStaffOrTargetUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny

# Create your views here.
@api_view(['POST'])
def create_auth(request):
    serialized = UserSerializer(data=request.data)
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    if serialized.is_valid():
        User.objects.create_user(
            serialized.init_data['email'],
            serialized.init_data['username'],
            serialized.init_data['password']
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model # If used custom user model
from .serializers import UserSerializer1

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer1