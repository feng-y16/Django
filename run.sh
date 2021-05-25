/usr/local/nginx/sbin/nginx -s stop
/usr/local/nginx/sbin/nginx
pkill -f uwsgi -9
uwsgi -i uwsgi.ini