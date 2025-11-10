from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.cart.models import Cart, CartItem


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order_from_cart(request):
    """Create an order from the current cart (session or user)."""
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Find cart
    cart = None
    if request.user and request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return Response({'detail': 'no cart'}, status=status.HTTP_400_BAD_REQUEST)
        cart = Cart.objects.filter(session_key=session_key).first()

    if not cart:
        return Response({'detail': 'cart not found or empty'}, status=status.HTTP_400_BAD_REQUEST)

    # Create order
    order = Order.objects.create(
        user=request.user if request.user and request.user.is_authenticated else None,
        cart=cart,
        shipping_address=serializer.validated_data.get('shipping_address', ''),
        total_amount=0,
    )

    total = 0
    # If items provided explicitly, use them; otherwise use cart items
    items_data = serializer.validated_data.get('items')
    if items_data:
        for it in items_data:
            p = it['product']
            q = it['quantity']
            oi = OrderItem.objects.create(order=order, product=p, quantity=q, unit_price=p.price)
            total += oi.subtotal()
    else:
        for ci in cart.items.all():
            oi = OrderItem.objects.create(order=order, product=ci.product, quantity=ci.quantity, unit_price=ci.unit_price)
            total += oi.subtotal()

    order.total_amount = total
    order.save()

    # Optionally: clear cart
    cart.items.all().delete()

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
