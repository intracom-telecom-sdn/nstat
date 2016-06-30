#!/bin/bash

# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

# If Beryllum zip exists in /opt, it extracts it in the
# current directory (the "fast" path).
# If it doesn't exist, it downloads it in /opt and them extracts it.

IMAGE_NAME='nstat'
sudo docker build --no-cache -t $IMAGE_NAME .
#sudo docker run -it nstat /bin/bash