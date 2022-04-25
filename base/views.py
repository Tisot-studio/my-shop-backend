from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import  Product, Order, OrderItem, ShippingAddress
from .serializers import ProductSerializer, OrderSerializer


# All products
@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# Get product by id
@api_view (['GET'])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response (serializer.data)


# Create an order
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user 
    data = request.data
    
    orderItems = data['orderItems']
    
    if orderItems and len(orderItems) == 0:
        return Response({'details' : 'No oder Items'}, status = status.HTTP_400_BAD_REQUEST)
    else:
        # Add order to db
        order = Order.objects.create(
            user=user,
            paymentMethod = data['paymentMethod'],
            phoneNumber = data['phone'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            orderPrice = data['orderPrice'],            
        )
        # Add address to db
        shipping = ShippingAddress.objects.create(
            user=user,
            order = order,
            city = data['city'],
            street = data['street'],
            house = data['house'],
            postalCode = data['postalCode'],
        )
        
        for i in orderItems:
            product = Product.objects.get(_id=i['_id'])
            item = OrderItem.objects.create(
                product=product,
                order=order,
                title = product.title,
                qty = i['quantity'],
                price=i['price'],
                image=product.imageCover              
            )
        product.available -= item.qty
        product.save()
    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)


# Get order by id 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
  user= request.user                    
  try:
    order = Order.objects.get(_id=pk)
    if user.is_staff or order.user == user:         
      serializer = OrderSerializer(order, many=False)  
      return Response(serializer.data)     
    else:
      Response({'detail': 'Not authorized to view this order'}, status=status.HTTP_400_BAD_REQUEST)
  except:
    return Response({'detail':'Order does not exist'},status=status.HTTP_400_BAD_REQUEST )


# Get user orders 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
  user= request.user
  orders = user.order_set.all()  
  serializer = OrderSerializer(orders, many=True)                 
  return Response(serializer.data)









