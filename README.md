
## 这是一个用户登录和注册教学项目
## 这是一个可重用的登录和注册APP

## 简单的使用方法：


* 创建虚拟环境
* 使用pip安装第三方依赖
* 修改settings.example.py文件为settings.py
* 运行migrate命令，创建数据库和数据表
* 运行python manage.py runserver启动服务器


路由设置：

```python
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from login import views  
  
def index(request):
    return HttpResponse(b'Welcome to Here')
  
urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('captcha/', include('captcha.urls')),
    path('confirm/', views.user_confirm),
    path('email_ack/', views.email_ack),
]
```