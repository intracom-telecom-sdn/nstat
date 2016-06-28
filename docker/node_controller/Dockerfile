FROM ubuntu:14.04

ENV export http_proxy='http://172.28.40.9:3128'
ENV export https_proxy='http://172.28.40.9:3128'
ENV export ftp_proxy='http://172.28.40.9:3128'
ENV no_proxy 127.0.0.1,localhost

RUN echo 'Acquire::http::Proxy "http://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::ftp::Proxy "ftp://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf

# Create a docker user with docker password and passwordless sudo privileges
# -----------------------------------------------------------------------------
RUN sudo useradd -m -s /bin/bash -p $(openssl passwd -crypt docker) -U docker
RUN echo "docker ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers

# Install NSTAT necessary tools
#------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y git
RUN apt-get install --force-yes -y unzip
RUN apt-get install --force-yes -y wget
RUN apt-get install --force-yes -y net-tools

# Java installation
#------------------------------------------------------------------------------
RUN apt-get update
RUN apt-get install --force-yes -y openjdk-7-jdk
RUN apt-get install --force-yes -y openjdk-7-jre

# Install NSTAT
#------------------------------------------------------------------------------
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

RUN /bin/bash
