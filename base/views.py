from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import  Product, Order, OrderItem, ShippingAddress, User
from .serializers import ProductSerializer, UserSerializer, UserSerializerWithToken,  OrderSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from datetime import datetime


# Отправка сообщения
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        '''Теперь при звонке на user/login/ в ответ будет посылаться не только
        токен, но и никнейм пользователя и его емаил, что позволит проводить
        идентификацию на фронтенде '''
        
        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Регистрация пользователя
@api_view(['POST'])
def registerUser(request):
    data = request.data  
    try:
        '''Если все впорядке, то сохраняет данные из формы в БД'''
        user = User.objects.create(
            first_name = data['name'],
            username = data['email'],
            email = data['email'],
            password = make_password(data['password'])
        )
        serializer = UserSerializerWithToken(user, many=False)
        
        # Отправка новому пользователю письма с ссылкой для активации аккаунта
        # current_site = get_current_site(request).domain
        # relativeLink = reverse('email-verify')
        # absurl = 'http://'+ current_site + relativeLink + '?to=' + serializer.data['token']
        # email_body = 'Hi ' + data['name'] + ' Use link below \n' + absurl
        # mail={'email_body': email_body, 'subject': 'Verify your email', 'to': data['email']}
        # Util.send_email(mail) 

        
        
        return Response(serializer.data)
    except:
        '''Выводит ошибку если пользователь с таким емейлом уже зарегистрирован'''
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


# Обновление пользовательской информации
@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    
    data = request.data
    if data['name'] !='':
        user.name = data['name']
    if data['email'] !='':
        user.email = data['email']
    if data['password'] !='':
        user.password = make_password(data['password'])
    
    user.save()
    
    return Response(serializer.data)



# Идентифицированный пользователь
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


# Список всех пользователей из БД. Доступно только для админа.
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# Функции отображения для товаров
@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view (['GET'])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response (serializer.data)


# Функция отображения для заказов
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user 
    data = request.data
    
    orderItems = data['orderItems']
    
    if orderItems and len(orderItems) == 0:
        return Response({'details' : 'No oder Items'}, status = status.HTTP_400_BAD_REQUEST)
    else:
        # Создаем запись в табице Заказ
        order = Order.objects.create(
            user=user,
            paymentMethod = data['paymentMethod'],
            phoneNumber = data['phone'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            orderPrice = data['orderPrice'],            
        )
        # Создаем запись в табице Адрес для доставки
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


# Получаем информацию о заказе из БД по id заказа. 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
  user= request.user                    # 1
  try:
    order = Order.objects.get(_id=pk)
    if user.is_staff or order.user == user:         # 2
      serializer = OrderSerializer(order, many=False)  # 3
      return Response(serializer.data)        # 4
    else:
      Response({'detail': 'Not authorized to view this order'}, status=status.HTTP_400_BAD_REQUEST)
  except:
    return Response({'detail':'Order does not exist'},status=status.HTTP_400_BAD_REQUEST )


"""" 1. Получаем информацию по пользователю (через токен)
2. В случае когда пользователь Стаф или с пользователем связан какой-либо заказ 
3. то помещаем в сериалайзер заказ, id которого взят из строки url 
4. и после возвращаем данные из сериалайзера по конкретному закзау, для отправки на клиент 
Все остальное для отправки ошибки"""



# Получаем информацию о заказах конкретного пользователя. 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
  user= request.user
  orders = user.order_set.all()  
  serializer = OrderSerializer(orders, many=True)                 
  return Response(serializer.data)



# Обновление статуса заказа "оплачено".
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)
    
    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()
    
    # Отправляем письмо менеджеру магазина информацию, что заказ оплачен
    email_body = f'Заказ № {order._id} оплачен'
    mail={'email_body': email_body, 'subject': 'Заказ оплачен', 'to': 'iltit@yandex.ru'}
    Util.send_email(mail) 
    return Response('Order was paid')






