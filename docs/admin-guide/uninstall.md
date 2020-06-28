# UNINSTALL

Remove configuration 

sudo rm -rf /etc/nginx/sites-enabled/api.conf 
sudo rm -rf /etc/nginx/sites-enabled/front.conf 
sudo rm -rf /etc/supervisor/conf.d/api.conf 
sudo rm -rf /etc/supervisor/conf.d/celery.conf
sudo rm -rf .venv
sudo rm -rf front/src/build

