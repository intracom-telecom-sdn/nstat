## Creating a base image with packer

In order to create a base image using `packer` you must

1.  Install packer following the [install packer guide](https://www.packer.io/docs/installation.html)
2.  Edit the file `deploy/packer/scripts/update.sh` and configure the
    `http_proxy` variable according to the proxy settings of your environment.
    Leave it empty in case you do not have a proxy.
3.  From the path `deploy/packer` run the following command:

    ```bash
    packer build ubuntu-14.04-server-amd64.json
    ```