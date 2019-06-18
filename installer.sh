#!/bin/bash
SOFTWARE_LIST="python3;python3-pip;rabbitmq-server;rsync;nginx;supervisor;neo4j=1:3.4.0;elasticsearch=6.6.1;npm"

printf "\nInstalling neo4j..\n"
wget -O - https://debian.neo4j.org/neotechnology.gpg.key | apt-key add -
printf 'deb https://debian.neo4j.org/repo stable/' | tee -a /etc/apt/sources.list.d/neo4j.list
printf "\n...Done neo4j installation!!!"

printf "\nInstalling elasticSearch...\n"
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
printf "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | tee -a /etc/apt/sources.list
printf "\n... Done elastic Search Installation!!!"

printf "\nInstalling NATS Server, Gnatsd1.4.1...\n"
mkdir -p tmp
mkdir -p /srv/nats/bin/
wget -P tmp/ https://github.com/nats-io/gnatsd/releases/download/v1.4.1/gnatsd-v1.4.1-linux-amd64.zip
unzip -j tmp/gnatsd-v1.4.1-linux-amd64.zip -d /srv/nats/bin/
printf "\n... Done NATs Server Installation!!!"

mkdir -p logs
sudo apt-get update
flag=`which python3`
if [ ! $flag ]
then 
    printf "\nPlease install Python 3.3 or greater"
    exit
fi

ver=$(python3 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "33" ]; then
    printf "\nThis script requires python 3.3 or greater"
    exit 
fi

printf "\nInstalling required software from list ...\n"
IFS=';' list=($SOFTWARE_LIST)
for item in "${list[@]}"; do 
    flag=`which $item`
    if [ ! $flag ]
    then
        printf "$item installed...\n"
        apt-get -y install $item
    fi
done

PROJ_ROOT_PATH=$PWD

flag=`pip3 list | grep virtualenv |awk '{print $1}'`
if [ ! $flag ]
then 
    pip3 install virtualenv
fi


flag=`ls -d */ | grep scrm_venv`
python_path=`which python3`
if [ ! $flag ]
then
    virtualenv scrm_venv -p /usr/bin/python3
fi
mkdir -p /var/log/gunicorn
flag=`pip3 -V | awk '{print $4}'`
flag1=$PWD/scrm_venv
tmp1=`printf "${flag//\//\_}"`
tmp2=`printf "${flag1//\//\_}"`
if [[ "$tmp1" =~ "$tmp2" ]]; then
   printf "\n ERROR : Virtual environment already active, please exit and install"
else
    source scrm_venv/bin/activate
    printf "\n Installing required Python packages from  list ...\n"
    #install python packages
    pip3 install -r requirements.txt    

    cd $PROJ_ROOT_PATH/SCRM
    rm -rf *.db
    printf "\nInstalling Migrations ...\n"
    python manage.py makemigrations >/dev/null 2>&1
    python manage.py migrate >/dev/null 2>&1
    printf "from ums.models import ScfUser as User; User.objects.create_superuser(first_name='scf',email='scf@aricent.com',password='scfadmin')"|python manage.py shell
    cd $PROJ_ROOT_PATH
    chmod +x extra/*.sh
    eval "printf \"$(cat extra/gunicorn_tmp.conf)\"" >extra/scrm_gunicorn.conf
    eval "printf \"$(cat extra/scrm_nginx_tmp.conf)\"" >extra/scrm_nginx.conf
    eval "printf \"$(cat extra/config_tmp.ini)\"" >config.ini
    printf "\n... Migrations Installed!!!"


    printf "\nGenerating nginx self-signed certificate..."
    mkdir -p /etc/nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt 
    printf "\n...Done!!!"

    printf "\nUpdating IP in configuration ..."
    #cd $PROJ_ROOT_PATH
    sh ./update_ip.sh
    printf "\n... IP updated"


    printf "\nInstalling UI ... please make sure minton_assets.tar.gz is present in this directory"
#    tar -C SCRM/static -zxf minton_assets.tar.gz
    npm run --silent install
    printf "\n... Done"

    printf "\nInstalling services ..."
    cp extra/scrm_gunicorn.conf /etc/supervisor/conf.d/
    cp extra/scrm_nginx.conf /etc/nginx/sites-available/
    cp extra/neo4j.conf /etc/neo4j/neo4j.conf
    cp extra/gnatsd.config /srv/nats/
    rm -rf /etc/nginx/sites-enabled/default
    ln -s /etc/nginx/sites-available/scrm_nginx.conf /etc/nginx/sites-enabled/default

    printf "\nRunning Services ..."
    cp extra/nats_tmp.service /etc/systemd/system/nats.service 
    cp extra/elasticsearch_tmp.service /etc/systemd/system/elasticsearch.service
    cp extra/neo4j_tmp.service /etc/systemd/system/neo4j.service
    cd /etc/systemd/system
    systemctl enable nats.service
    systemctl enable elasticsearch.service
    systemctl enable neo4j.service
    systemctl start nats.service
    systemctl start elasticsearch.service
    systemctl start neo4j.service

    supervisorctl reread
    supervisorctl update
    service nginx restart
    printf "\n... Done"
    printf "\nStarting Applications ..."
    cd $PROJ_ROOT_PATH
    . scrm_venv/bin/activate
    cd SCRM
    sh ./restart.sh
    printf "\n... All Done !!"

fi
