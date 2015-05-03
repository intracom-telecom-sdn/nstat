FROM centos:centos7

RUN yum -y update
RUN yum clean all

# General deps
RUN yum -y install git unzip wget net-tools 

# ODL build deps
RUN yum -y install openssh java-1.7.0-openjdk java-1.7.0-openjdk-devel 

# cbench build deps
RUN yum -y install net-snmp net-snmp-devel libpcap-devel autoconf make automake libtool libconfig-devel 

# matplotlib 
RUN yum -y install python-matplotlib

# requests
RUN yum -y install python-requests

# psutil
RUN yum -y install python-devel
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install psutil

# download ODL Helium SR3 and store it under /opt
RUN wget https://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/0.2.3-Helium-SR3/distribution-karaf-0.2.3-Helium-SR3.zip -P /opt/

RUN yum clean all
