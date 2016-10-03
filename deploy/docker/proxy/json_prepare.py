# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reads  username/password/ip for all NSTAT nodes from docker-compose.yml
and prepares the final json input file to be used for docker-based testing"""

import yaml


def json_prepare(yaml_file, json_output_file):
    """Query number of hosts registered in ODL operational DS

    :param filename in yaml format
    :returns: number of hosts found, 0 if none exists and -1 in case of
    error.
    :rtype: int
    :type controller_nb_interface: namedtuple<str,int,str,str>
    """
    # load yaml file and read necessary data
    with open(yaml_file, 'r') as stream:
        try:
            dockerdata = yaml.load(stream)
            for dockerdatakey in dockerdata:
                if dockerdatakey == 'services':
                    servicesdata = dockerdata['services']
                    for servicesdatakey in servicesdata:
                        if servicesdatakey == 'nstat':
                            print(servicesdata[servicesdatakey])
                            nstatdata = servicesdata['nstat']
                        if servicesdatakey == 'controller':
                            print(servicesdata[servicesdatakey])
                            controllerdata = servicesdata['controller']
                        if servicesdatakey == 'nbgen':
                            print(servicesdata[servicesdatakey])
                            nbgendata = servicesdata['nbgen']
                        if servicesdatakey == 'mtcbench':
                            print(servicesdata[servicesdatakey])
                        if servicesdatakey == 'mn01':
                            print(servicesdata[servicesdatakey])
                        if servicesdatakey == 'mn02':
                            print(servicesdata[servicesdatakey])

        except yaml.YAMLError as exc:
            print(exc)

    # load json input file and write data to output file

if __name__ == '__main__':
    yaml_file = 'docker-compose.yml'
    json_output_file = 'beryllium_DS_sb_active_scalability_mtcbench'
    json_prepare(yaml_file,json_output_file)