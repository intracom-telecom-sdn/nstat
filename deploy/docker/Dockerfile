FROM ubuntu:14.04

ENV http_proxy='http://172.28.40.9:3128/'
ENV https_proxy='http://172.28.40.9:3128/'
ENV ftp_proxy='http://172.28.40.9:3128/'
ENV no_proxy 127.0.0.1,localhost

RUN echo 'Acquire::http::Proxy "http://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::ftp::Proxy "ftp://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://172.28.40.9:3128/";'| tee -a /etc/apt/apt.conf

RUN apt-get update
RUN apt-get install --force-yes -y wget
RUN chmod 777 -R /opt
RUN apt-get update
RUN cd /opt
RUN wget https://raw.githubusercontent.com/intracom-telecom-sdn/nstat/master/deploy/provision.sh
RUN chmod +x provision.sh
RUN /bin/bash -c "./provision.sh"
RUN cd /proc/sys/kernel/pty
RUN echo "50000" > max
RUN /bin/bash