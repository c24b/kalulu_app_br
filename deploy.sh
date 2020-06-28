#!/bin/bash
ROOT_DIR=$(pwd)
VENV=$ROOT_DIR/.venv
install_certbot(){
    sudo apt-get install certbot python-certbot-nginx
}

restart_services(){
    echo "=========================="
    echo "      RESTART SERVICES    "
    echo "=========================="
    echo "- restart redis"
    
    sudo systemctl restart redis-server
    sudo systemctl restart redis
    echo "- restart nginx"
    
    sudo nginx -t
    sudo systemctl restart nginx
    sudo nginx status
    echo "- restart supervisorctl"
    sudo supervisorctl reread
    sudo supervisorctl update all
    sudo supervisorctl start all
    sudo supervisorctl status
    echo "================================"
}


install_front(){
    echo "=========================="
    echo "      INSTALL FRONT       "
    echo "=========================="
    cd $ROOT_DIR/front/
    echo "- install node dependencies"
    
    npm install
    echo "-build Vue.Js app"
    
    npm run build
    echo '[*] OK'   
    cd $ROOT_DIR
    echo "================================"
}

echo "=========================="
trap "exit" INT
# install_certbot
install_front
restart_services
