from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None, **extra_fields):
        user = self.create_user(name, email, password=password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user 
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, default=None)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=255, default='')

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def get_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email


class Product(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    imageCover = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    available = models.IntegerField(null=True, blank=True, default=0)
    
    def __str__(self):
        return self.title
    
    
class Order(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paymentMethod= models.CharField(max_length=200, null=True, blank=True)
    phoneNumber= models.CharField(max_length=15, null=True, blank=True)
    taxPrice= models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    shippingPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    orderPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return str(self._id)
    
    
class OrderItem(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    product= models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    
    def __str__(self):
        return str(self.title)
    
    
class ShippingAddress(models.Model):
    _id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    house = models.CharField(max_length=200, null=True, blank=True)
    postalCode = models.CharField(max_length=200, null=True, blank=True)
    shippingPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.street)
    


    
