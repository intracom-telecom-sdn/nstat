# Update the box
useradd -m -s /bin/bash -p $(openssl passwd -crypt jenkins) -U jenkins
echo "jenkins ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers

http_proxy=http://172.28.40.9:3128/
https_proxy=$http_proxy

# Bipass proxy settings if http_proxy is empty
if [ ! -z "$http_proxy" ]
then
    export http_proxy
    export https_proxy

    echo "http_proxy=$http_proxy" | sudo tee -a /etc/environment
    echo "https_proxy=$https_proxy" | sudo tee -a /etc/environment
    echo "HTTP_PROXY=$http_proxy" | sudo tee -a /etc/environment
    echo "HTTPS_PROXY=$https_proxy" | sudo tee -a /etc/environment
    if [ ! -f /etc/apt/apt.conf ]; then
        sudo touch /etc/apt/apt.conf
    fi
    echo 'Acquire::http::Proxy "'$http_proxy'";' | sudo tee -a /etc/apt/apt.conf
    echo 'Acquire::https::Proxy "'$https_proxy'";' | sudo tee -a /etc/apt/apt.conf
fi

sudo apt-get -y update
sudo apt-get -y upgrade
