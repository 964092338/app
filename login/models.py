from django.db import models

# Create your models here.


class User(models.Model):

    gender = (
        ('male', '男'),
        ('female', '女')
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.CharField(max_length=128, unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    def __repr__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = '用户'
        verbose_name_plural = "用户"

    __str__ = __repr__

class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "{}: {}".format(self.user.name, self.code)

    class Meta:
        ordering = ["-c_time"]
        verbose_name = '确认码'
        verbose_name_plural = '确认码'

    __str__ = __repr__