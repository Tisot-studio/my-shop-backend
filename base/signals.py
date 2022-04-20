from django.db.models.signals import pre_save
# from django.contrib.auth.models import User
from .models import User

'''Утилита позволяющая обновлять никнейм пользователя делая его таким же как и емайл,
обновление происходит каждый раз, когда пользователь обновляет (сохраняет) информацию о себе'''
def updateUser(sender, instance, **kwarg):
    user = instance
    if user.email != '':
        user.username = user.email
    
pre_save.connect(updateUser, sender=User)