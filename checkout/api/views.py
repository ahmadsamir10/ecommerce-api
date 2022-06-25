from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from checkout.models import OrderProduct, Order
from users.api.permissions import StaffNotAllowed
from dashboard.api.serializers import OrderProductSerializer as ListRetrieveOrderProductSerializer
from .serializers import OrderProductSerializer, OrderSerializer





class ProductOrderView(ModelViewSet):
    serializer_class = OrderProductSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    
    def get_queryset(self):
        user = self.request.user
        queryset = OrderProduct.objects.filter(user=user)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance_id = serializer.data['id']
        instance = OrderProduct.objects.get(id=instance_id)
        new_serializer = ListRetrieveOrderProductSerializer(instance=instance)
        headers = self.get_success_headers(new_serializer.data)
        return Response(new_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ListRetrieveOrderProductSerializer(queryset, many=True)
        return Response(serializer.data)    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ListRetrieveOrderProductSerializer(instance)
        return Response(serializer.data)
    
    
class OrderView(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'trace']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.prefetch_related('products__product', 'products__color', 'products__size').filter(user=user)
        
        return queryset 
    
    