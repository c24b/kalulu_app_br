#!/bin/bash

ROOT_DIR=$(pwd)
VENV=$ROOT_DIR/.venv

install_mongo()
{
    #remove previous install in case
    sudo rm /etc/apt/sources.list.d/mongodb-org-4.2.list
    sudo rm /etc/apt/sources.list.d/mongodb.list
    sudo apt-get -qq install -y libc6 gnupg
    wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
    echo "deb http://repo.mongodb.org/apt/debian "$(lsb_release -sc)"/mongodb-org/4.2 main" | sudo tee /etc/apt/sources.list.d/mongodb.list
    sudo apt-get -qq update
    sudo apt-get -qq  install -y mongodb-org
    # mongod --config $ROOT_DIR/conf/templates/mongod.conf 
    sudo systemctl start mongod.service
    sudo systemctl enable mongod.service
    
}

install_node()
{
    
    # sudo apt-get install git-core curl build-essential openssl libssl-dev -y
    # sudo apt-get install curl software-properties-common -y
    # sudo apt-get install build-essential -y
    # sudo apt-get install gcc g++ make -y
    curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    sudo apt-get install -yqq nodejs
    # git clone https://github.com/joyent/node.git /usr/bin/node
    # cd /usr/bin/node
    # ./configure
    # make
    # sudo make install
    echo "Node version" + $(node -v)
    # curl -L https://npmjs.org/install.sh | sudo sh
    echo "NPM Version" + $(npm -v)
    # old version
    # sudo apt-get install git-core curl build-essential openssl libssl-dev -y
    # sudo apt-get install curl software-properties-common -y
    # sudo apt-get install build-essential -y
    # curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    # sudo apt-get install nodejs -y
    # echo "NODE:" $(node -v)
    # echo "NPM:" $(npm -v)
    continue
}

install_dependencies()
{
    echo "=========================="
    echo " INSTALL DEPENDENCIES     "
    echo "=========================="
    sudo apt -qq install build-essential -y
    DEPENDENCIES=('nginx' 'supervisor' 'redis-server' 'python3' 'python3-pip' 'python3-dev', 'mkdocs')
    echo "Installing dependencies"
    for pkg in "${DEPENDENCIES[@]}" 
    do
        echo ">>>>>>" $pkg
        echo $(dpkg-query -W -f='${Status}\n' $pkg) 
        dpkg -s "${pkg}" >/dev/null 2>&1 || sudo apt-get -yqq install $pkg
        
    done
    #MONGO
    echo ">>>>> mongo"
    sudo apt-get -qq install -y libc6 gnupg
    wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
    echo "deb http://repo.mongodb.org/apt/debian "$(lsb_release -sc)"/mongodb-org/4.2 main" | sudo tee /etc/apt/sources.list.d/mongodb.list
    sudo apt-get -qq update
    sudo apt-get -qq  install -y mongodb-org
    service mongod start
    # NODE
    echo ">>>>> nodejs + npm"
    curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    sudo apt-get -qq update
    sudo apt-get install -yqq nodejs
    sudo apt-get -qq autoremove    
}

create_files_dir(){
    echo "=========================="
    echo "     INSTALL FILES DIR    "
    echo "=========================="
    # FILES_DIRS = [$ROOT_DIR/files/archived,$ROOT_DIR/files/clean, $ROOT_DIR/files/raw, $ROOT_DIR/files/dumps]
    # for fdir in "${FILES_DIRS[@]}" 
    # do 
    #     echo ">>>>" $fdir
    #     if [ -f "$fdir" ]; then
    #         echo " Exists"
    #     else
    #         mkdir -p $fdir
    #     fi
    # done
}

install_app(){
    echo "=========================="
    echo "   INSTALL BACK+API       "
    echo "=========================="
    # rm -rf $VENV
    FILE=$VENV/bin/activate
    if [ -f "$FILE" ]; then
        echo "  Exists. Skip virtual env install update packages" 
        $VENV/bin/pip install -e .
        $VENV/bin/pip install -r $ROOT_DIR/conf/requirements.txt
    else
        sudo apt-get -yq install virtualenv 
        virtualenv --python=python3 --no-site-packages .venv
        $VENV/bin/pip install -e .
        $VENV/bin/pip install -r $ROOT_DIR/conf/requirements.txt
        echo '[*] OK'
        echo "================================"
    fi
}
test(){
    $VENV/bin/python tests/test_activity.py
}

install_front(){
    echo "=========================="
    echo "      INSTALL FRONT       "
    echo "=========================="
    cd $ROOT_DIR/front/
    npm install
    npm run build
    echo '[*] OK'   
    cd $ROOT_DIR
    echo "================================"
}

install_certbot(){
    sudo apt-get install certbot python-certbot-nginx
}

install_docs(){
    echo "=========================="
    echo "      INSTALL DOC       "
    echo "=========================="
    cd $ROOT_DIR
    sudo $VENV/bin/mkdocs build
    echo '[*] OK'   
    echo "================================"
}
# db_run()
# {
#     echo "INIT DB"
#     $ROOT_DIR/.venv/bin/python $ROOT_DIR/db/run.py $cmd_option
# }


run()
{
    echo "=========================="
    echo "      INIT DB             "
    echo "=========================="
    # systemctl mongod status
    $ROOT_DIR/.venv/bin/python $ROOT_DIR/db/run.py &
    echo '[*] OK'
    echo "================================"
}

initialize_database_from_files()
{
    echo "=========================="
    echo "   INIT DB with files     "
    echo "=========================="
    systemctl mongod status
    $ROOT_DIR/.venv/bin/python $ROOT_DIR/db/run.py &
    echo '[*] OK'
    
    echo "================================"
}

dump_database()
{
    echo "=========================="
    echo "          DUMP DB         "
    echo "=========================="
    mongodump --db kalulu --gzip $ROOT_DIR/files/dumps/
    echo "================================"    
}
restore_database()
{
    echo "=========================="
    echo "          RESTORE DB      "
    echo "=========================="
    mongorestore --db kalulu --gzip $ROOT_DIR/files/dumps/
    echo "================================"
}

archive_files(){
    echo "=========================="
    echo "       ARCHIVE DB         "
    echo "=========================="
    rm -rf $ROOT_DIR/files/old/clean;
    rm -rf $ROOT_DIR/files/old/raw;
    mv  $ROOT_DIR/files/clean $PWD/files/old/clean;
    mv  $ROOT_DIR/files/raw $PWD/files/old/raw; 
    echo "================================"
}

install_crontab()
{
    echo "=========================="
    echo "     INSTALL CRONTAB      "
    echo "=========================="
    echo '== Creating a crontab for DB update =='
    sudo touch /var/spool/cron/$USER
    echo "3 3 * * 3 $VENV/bin/python $ROOT_DIR/back/run.py" >> /var/spool/cron/$USER
    sudo crontab -u $USER -l
    echo "================================"
}


restart_services(){
    echo "=========================="
    echo "      RESTART SERVICES    "
    echo "=========================="
    sudo systemctl restart redis-server
    sudo systemctl restart redis
    sudo nginx -t
    sudo systemctl restart nginx
    sudo nginx status
    sudo supervisorctl reread
    sudo supervisorctl update all
    sudo supervisorctl start all
    sudo supervisorctl status
    echo "================================"
}

configure(){
    echo "=========================="
    echo "       CONFIGURE          "
    echo "=========================="
    sudo $VENV/bin/python $ROOT_DIR/utils/install.py
}


echo "=========================="
trap "exit" INT
install_certbot
create_files_dir
install_dependencies
install_app
configure
install_front
# prebuild docs 
# install_docs
restart_services
# run