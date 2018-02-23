部署生产环境：
修改 SwhyDataAnalytic.SwhyDataAnalytic.settings.py中
STATIC_ROOT = 'D:/Project/Python/SwhyDataAnalytic'为物理路径/usr/local/SwhyDataAnalytic/static/

如果修改static文件夹位置，需要修改vim /etc/nginx/nginx.conf中，static位置

开启nginx服务
service nginx  start

uwsgi django_socket.ini

退出
screen
python manage.py runserver 0.0.0.0:8000
ctrl+a d
进入
screen -r

压缩上一版本
tar -zcvf /usr/local/SwhyDataAnalytic.tar.gz /usr/local/SwhyDataAnalytic

Restful接口开发完，发布操作
makemigrations [appname] 
migrate

重置migrations
migrate –-fake XXX
makemigrations XXX


