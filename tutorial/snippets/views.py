# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer, IncredibleInputSerializer
from rest_framework import mixins
from rest_framework import generics
from django.contrib.auth.models import User
from snippets.serializers import UserSerializer
from rest_framework import permissions
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.views import APIView
from rest_framework import filters
@api_view(['GET'])
def api_root(request, format=None):
    return Response({   
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })

class IncredibleView(APIView):
    def get(self, request):
        # Validate the incoming input (provided through query parameters)
        serializer = IncredibleInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # Get the model input
        data = serializer.validated_data
        city = data["city"]
        state = data["state"]
        n_days = data["n_days"]
        # model_input2 = data["n_days2"]
        # Perform the complex calculations
        complex_result = city+state+n_days + "xyz"
        # Return it in your custom format
        return Response({
            "complex_result": complex_result,
        })

class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Create your views here.
#use mixins and generic api view!
# class SnippetList(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   generics.GenericAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# class SnippetDetail(mixins.RetrieveModelMixin, 
#                     mixins.UpdateModelMixin, 
#                     mixins.DestroyModelMixin, 
#                     GenericAPIView):
    
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     def get(self, request, *args, **kwargs):
#         return self.retrive(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.detroy(request, *args, **kwargs)

#use class based api view
# class SnippetList(APIView):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         snippets = Snippet.objects.all()[:5] 
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class SnippetDetail(APIView):
#     """
#     List all snippets, or create a new snippet.
#     """
#     def get_object(self, pk):
#         try:
#             snippet = Snippet.objects.get(pk=pk)
#             return snippet
#         except Snippet.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delet(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)




