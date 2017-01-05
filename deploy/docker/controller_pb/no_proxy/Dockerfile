FROM ubuntu:14.04

ENV http_proxy=

RUN apt-get update

RUN apt-get install --force-yes -y openssh-server
RUN apt-get install --force-yes -y openssh-client
RUN apt-get install --force-yes -y openssl
RUN apt-get install --force-yes -y net-tools
RUN apt-get install --force-yes -y unzip
RUN apt-get install --force-yes -y bzip2
RUN apt-get install --force-yes -y python3-lxml

RUN apt-get update
RUN apt-get install --force-yes -y wget
RUN chmod 777 -R /opt
RUN apt-get install --force-yes -y software-properties-common
#RUN apt-get update
#RUN apt-get install --force-yes -y openjdk-7-jdk
RUN add-apt-repository ppa:openjdk-r/ppa -y
RUN apt-get update
RUN apt-get install --force-yes -y openjdk-8-jdk
#RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-8-openjdk-amd64/ 1100

# ------------------------------------------------------------------------------
# OFTRAF
# ------------------------------------------------------------------------------
RUN wget -P /opt/ https://raw.githubusercontent.com/intracom-telecom-sdn/oftraf/master/deploy/provision.sh
RUN mv /opt/provision.sh /opt/provision_oftraf.sh
RUN chmod +x /opt/provision_oftraf.sh
RUN /bin/bash -c "/opt/provision_oftraf.sh"

# ------------------------------------------------------------------------------
# ODL PREBuilt controllers
# ------------------------------------------------------------------------------
RUN wget -P /opt/ https://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/0.4.0-Beryllium/distribution-karaf-0.4.0-Beryllium.zip
RUN wget -P /opt/ https://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/0.5.0-Boron/distribution-karaf-0.5.0-Boron.zip
RUN wget -P /opt/ https://nexus.opendaylight.org/content/repositories/public/org/opendaylight/integration/distribution-karaf/0.4.3-Beryllium-SR3/distribution-karaf-0.4.3-Beryllium-SR3.zip


# Configure ssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:root123' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN mkdir -p /home/root/.ssh
RUN touch /home/root/.ssh/known_hosts
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
