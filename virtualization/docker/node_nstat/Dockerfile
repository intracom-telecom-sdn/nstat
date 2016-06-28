FROM ubuntu:14.04

ENV export http_proxy='http://172.28.40.9:3128'
ENV export https_proxy='http://172.28.40.9:3128'
ENV export ftp_proxy='http://172.28.40.9:3128'
ENV no_proxy 127.0.0.1,localhost

RUN echo 'Acquire::http::Proxy "http://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::ftp::Proxy "ftp://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf

# Create a docker user with docker password and passwordless sudo privileges
# ------------------------------------------------------------------------------
RUN sudo useradd -m -s /bin/bash -p $(openssl passwd -crypt docker) -U docker
RUN echo "docker ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers

# Install NSTAT necessary tools
#-------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y git
RUN apt-get install --force-yes -y unzip
RUN apt-get install --force-yes -y wget
RUN apt-get install --force-yes -y iperf
RUN apt-get install --force-yes -y mz
RUN apt-get install --force-yes -y wireshark
RUN apt-get install --force-yes -y net-tools

# build tools
#-------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y build-essential
RUN apt-get install --force-yes -y snmp
RUN apt-get install --force-yes -y libsnmp-dev
RUN apt-get install --force-yes -y snmpd
RUN apt-get install --force-yes -y libpcap-dev
RUN apt-get install --force-yes -y autoconf
RUN apt-get install --force-yes -y make
RUN apt-get install --force-yes -y automake
RUN apt-get install --force-yes -y libtool
RUN apt-get install --force-yes -y libconfig-dev

# ssh service & java installation
#-------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y openjdk-7-jdk
RUN apt-get install --force-yes -y openjdk-7-jre

# Python installation
#-------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y python-dev
RUN apt-get install --force-yes -y python-setuptools
RUN apt-get install --force-yes -y python3.4-dev
RUN apt-get install --force-yes -y python3-setuptools
RUN apt-get install --force-yes -y python
RUN apt-get install --force-yes -y python3.4
RUN apt-get install --force-yes -y python-pip
RUN apt-get install --force-yes -y python3-pip

# Upgrade python setuptools and pip
#-------------------------------------------------------------------------------
RUN pip install --upgrade pip
RUN pip3 install --upgrade pip3
RUN pip install --upgrade setuptools
RUN pip3 install --upgrade setuptools

# Install Python libraries
#-------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y python3-bottle
RUN apt-get install --force-yes -y python3-requests
RUN apt-get install --force-yes -y python3-matplotlib
RUN apt-get install --force-yes -y python3-lxml
RUN apt-get install --force-yes -y python-lxml
RUN apt-get install --force-yes -y python-paramiko
RUN apt-get install --force-yes -y python-pypcap
RUN apt-get install --force-yes -y python-dpkt
RUN apt-get install --force-yes -y python-bottle

# Install NSTAT necessary python3.4 tools
#-------------------------------------------------------------------------------
RUN easy_install3 pip
RUN pip3 install paramiko
RUN pip3 install collections-extended

# Install Mininet
#-------------------------------------------------------------------------------
RUN apt-get update && apt-get install --force-yes -y uuid-runtime
RUN git clone https://github.com/mininet/mininet.git
RUN cd mininet
RUN git checkout -b 2.2.1 2.2.1
RUN ./util/install.sh -n3f

# Install NSTAT
#-------------------------------------------------------------------------------
RUN git clone https://github.com/intracom-telecom-sdn/nstat.git /home/docker/nstat
RUN cd /home/docker/nstat
RUN git branch -a # list NSTAT branches
RUN git checkout master # checkout to master branch
RUN git tag -l # list NSTAT tags

# ssh service
#------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y openssh-client
RUN apt-get install --force-yes -y openssh-server
RUN service ssh start

RUN ./util/install.sh -V 2.3.0
RUN service openvswitch-switch start
RUN service openvswitch-switch start
RUN /bin/bash
