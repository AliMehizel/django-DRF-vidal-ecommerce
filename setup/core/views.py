from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
# stripe
import stripe
from decimal import *



stripe.api_key = ''


# Stripe payment process
class PaymentView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        # Retrieve the order details from the request data
        data = request.data['oreder_id']
        # get oreder after request
        if data != '':
            oreder = Oreder.objects.get(id=data)
            orederItem = oreder.orederitem_set.all()

        else:
            return Response('cart items empty')

        # iterate through catitems and add each item deatils to line items for stripe
        line_items = []
        for item in orederItem:

            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{item.product.name}',

                    },
                    'unit_amount': int(item.product.price*100),

                },
                'quantity': item.quantity,
            },)

        session = stripe.checkout.Session.create(
            # iterate throw data
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:5173/',
            cancel_url='http://localhost:5173/cart-items',
        )
        tran_id = session.id

        # save transaction id in oreder table
        oreder.stripe_oreder_id = tran_id
        oreder.save()
        return Response({'url': session.url})


# Authentication process
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.name
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# Get all products
@api_view(['GET'])
def GetAllProduct(request, format=None):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Get prodct details
@api_view(['GET'])
def GetProduct(request, pk, format=None):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Get product by filtring category
@api_view(['GET'])
def GetByCategory(request, category, format=None):
    product = Product.objects.filter(category=category)
    serializer = ProductSerializer(product, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Add product To cart
@api_view(['POST'])
def AddToCart(request, format=None):
    product = request.data['name']
    size = request.data['size']
    color = request.data['color']
    # get product from product model
    get_product = get_object_or_404(Product, name=product)
    # get oreder else create
    oreder, create = Oreder.objects.get_or_create(complete=False)
    # filter oreder item
    orederItem = OrederItem.objects.filter(
        oreder=oreder, product=get_product, color=color, size=size)
    if orederItem:
        # orederItem[0] access the first element in queryset
        orederItem[0].quantity += 1
        orederItem[0].save()
    else:
        OrederItem.objects.create(
            oreder=oreder, product=get_product, color=color, size=size)

    product_added = OrederItem.objects.get(oreder=oreder, product=get_product)
    serializer = OrederItemSerializer(product_added, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Edit Quantity
@api_view(['POST'])
def UpdateQte(request, format=None):
    action = request.data['action']
    product = request.data['name']
    print(action)
    # get product from product model
    get_product = get_object_or_404(Product, name=product)
    # get oreder else create
    oreder, create = Oreder.objects.get_or_create(complete=False)
    orederItem = OrederItem.objects.filter(oreder=oreder, product=get_product)

    if orederItem:
        if action == 'add':
            orederItem[0].quantity += 1
        elif action == 'remove':
            orederItem[0].quantity -= 1
            if orederItem[0].quantity < 1:
                product = OrederItem.objects.get(
                    oreder=oreder, product=get_product)
                orederItem.delete()  # we need to return to rest of data to filter the deleted item on front
                return Response(status=status.HTTP_204_NO_CONTENT)

        orederItem[0].save()

    product_updated = OrederItem.objects.get(
        oreder=oreder, product=get_product)
    serializer = OrederItemSerializer(product_updated, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



# Get Cart Item
@api_view(['GET'])
def GetCartItem(request, format=None):
    # get oreder else create
    oreder, create = Oreder.objects.get_or_create(complete=False)
    orederItem = oreder.orederitem_set.all()
    serializer = OrederItemSerializer(orederItem, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Delete from cart
@api_view(['DELETE'])
def DeleteFromCart(request, pk, format=None):
    orederItem = OrederItem.objects.get(pk=pk)

    orederItem.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# Shipping adress view
class AddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        customer = request.user
        oreders, create = Oreder.objects.get_or_create(complete=False)
        oreders.complete = True
        oreders.customer = customer
        oreders.save()
        data = request.data

        ShippingAddress.objects.create(
            customer=customer,
            oreder=oreders,
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zipcode=data['zipcode']
        )
        address = ShippingAddress.objects.all()
        serializer = AddressSerializer(address, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
