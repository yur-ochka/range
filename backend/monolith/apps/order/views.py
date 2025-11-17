from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from apps.cart.models import Cart


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('items__product')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderAdminListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().select_related('user').prefetch_related('items__product')


class OrderStatusUpdateView(generics.GenericAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data['status']
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class OrderStatusLookupView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    queryset = Order.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if not self._has_access(request, order):
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _has_access(request, order):
        if request.user and request.user.is_authenticated:
            if request.user.is_staff or order.user_id == request.user.id:
                return True

        email = request.query_params.get('email', '')
        if email:
            email = email.strip().lower()
            if order.contact_email and order.contact_email.lower() == email:
                return True
            if order.user and order.user.email.lower() == email:
                return True

        return False


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order_from_cart(request):
    """Create an order from the current cart (session or user)."""
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = request.user if request.user and request.user.is_authenticated else None

    # Determine contact info for the order (guest checkout supported)
    contact_email = serializer.validated_data.get('contact_email') or (user.email if user else '')
    contact_phone = serializer.validated_data.get('contact_phone', '').strip()
    contact_name = serializer.validated_data.get('contact_name', '').strip()
    if user:
        full_name = user.get_full_name().strip() if hasattr(user, 'get_full_name') else ''
        if not contact_name:
            contact_name = full_name or user.first_name or user.username or ''
        if not contact_phone and hasattr(user, 'profile'):
            contact_phone = user.profile.phone or ''
    shipping_address = serializer.validated_data.get('shipping_address', '').strip()

    # Resolve items either from payload or cart
    items_data = serializer.validated_data.get('items', [])
    cart = None
    used_cart_items = False

    if not items_data:
        if user:
            cart = Cart.objects.filter(user=user).prefetch_related('items__product').first()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).prefetch_related('items__product').first()
        if not cart or not cart.items.exists():
            return Response({'detail': 'cart not found or empty'}, status=status.HTTP_400_BAD_REQUEST)
        items_data = [
            {'product': item.product, 'quantity': item.quantity, 'unit_price': item.unit_price}
            for item in cart.items.all()
        ]
        used_cart_items = True
    else:
        # ensure unit price resolved when creating from payload
        items_data = [
            {'product': entry['product'], 'quantity': entry['quantity'], 'unit_price': entry['product'].price}
            for entry in items_data
        ]

    order = Order.objects.create(
        user=user,
        cart=cart,
        shipping_address=shipping_address,
        contact_email=contact_email,
        contact_phone=contact_phone,
        contact_name=contact_name,
        total_amount=0,
    )

    total = 0
    for item in items_data:
        product = item['product']
        quantity = item['quantity']
        unit_price = item['unit_price']
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )
        total += order_item.subtotal()

    order.total_amount = total
    order.save(update_fields=['total_amount', 'updated_at'])

    if used_cart_items and cart:
        cart.items.all().delete()

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
