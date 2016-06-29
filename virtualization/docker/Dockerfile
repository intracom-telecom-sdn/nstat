FROM ubuntu:14.04

ENV export http_proxy='http://172.28.40.9:3128/'
ENV export https_proxy='http://172.28.40.9:3128/'
ENV export ftp_proxy='http://172.28.40.9:3128/'
ENV no_proxy 127.0.0.1,localhost


RUN cd ~
RUN echo "export http_proxy='http://172.28.40.9:3128/'" | tee -a ./bashrc
RUN echo "export https_proxy='http://172.28.40.9:3128/'" | tee -a ./bashrc
RUN echo "export ftp_proxy='http://172.28.40.9:3128/'" | tee -a ./bashrc
RUN echo "no_proxy 127.0.0.1,localhost" | tee -a ./bashrc

RUN echo 'Acquire::http::Proxy "http://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::ftp::Proxy "ftp://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf
RUN echo 'Acquire::https::Proxy "https://172.28.40.9:3128/";' | tee -a /etc/apt/apt.conf

RUN /bin/bash
