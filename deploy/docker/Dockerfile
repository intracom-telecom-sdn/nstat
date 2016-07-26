FROM ubuntu:14.04

ENV http_proxy='http://172.28.40.9:3128/'
ENV https_proxy='http://172.28.40.9:3128/'

ENV no_proxy='127.0.0.1,localhost'

RUN echo 'Acquire::http::Proxy "http://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf

RUN echo 'Acquire::https::Proxy "https://172.28.40.9:3128/";'| tee -a /etc/apt/apt.conf

RUN apt-get update
RUN apt-get install --force-yes -y wget
RUN chmod 777 -R /opt
RUN apt-get update
RUN cd /opt
RUN wget https://raw.githubusercontent.com/intracom-telecom-sdn/nstat/develop_provision_review/deploy/provision.sh
RUN chmod +x provision.sh
RUN /bin/bash -c "./provision.sh"
CMD ["service", "openvswitch-switch" "start"]

# Configure ssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:screencast' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
CMD ["/usr/sbin/sshd", "-D"]
