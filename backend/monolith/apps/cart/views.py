from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer


def _get_or_create_cart(request):
    # If user is authenticated, prefer user cart
    if request.user and request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    # Otherwise use session key
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


class CartView(APIView):
    def get(self, request):
        cart = _get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemAddView(APIView):
    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        cart = _get_or_create_cart(request)

        # If an item already exists for this product, increase quantity
        existing = CartItem.objects.filter(cart=cart, product=product).first()
        if existing:
            existing.quantity += quantity
            existing.save()
            out = CartItemSerializer(existing)
            return Response(out.data, status=status.HTTP_200_OK)

        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            unit_price=product.price,
        )

        out = CartItemSerializer(item)
        return Response(out.data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    def patch(self, request, item_id):
        cart = _get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        qty = request.data.get('quantity')
        if qty is None:
            return Response({'detail': 'quantity required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            return Response({'detail': 'quantity must be integer'}, status=status.HTTP_400_BAD_REQUEST)
        if qty <= 0:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        item.quantity = qty
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, item_id):
        cart = _get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
