## Creating a base image with packer

In order to create a base image using `packer` you must

1.  Install packer following the [install packer guide](https://www.packer.io/docs/installation.html)
2.  From the path `deploy/packer` run the following command:

    ```bash
    packer build ubuntu-14.04-server-amd64.json
    ```

After the completion in folder `build_output` will get the result of the build.