# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Contains data structure of report element and tables inside the report.
These are used to generate the html report """

import collections

class ReportSpec(object):
    """Contains the specification of the html report, the title of the
    report, the json files of the configuration and data and the lists of
    tables to be generated in the report.
    """

    def __init__(self, config_json, results_json, title, config_tables,
                 results_table):
        """
        :param config_json: string containing the file path to the
        json file containing the configuration parameters of the test.
        :param results_json: string containing the file path to the json file
        with the results of the experiment.
        :param title: string containing the Title of the generated html result
        page.
        :param config_tables : Contains TableSpec objects of configuration
        tables, that will be inserted inside the generated html report.
        :param results_table: Contains TableSpec objects of result tables,
        that will be inserted inside the generated html report.
        :type config_json: str
        :type results_json: str
        :type title: str
        :type config_tables: list<TableSpec>
        :type results_table: list<TableSpec>
        """

        self.config_json = config_json
        self.results_json = results_json
        self.title = title

        # A list of tableSpec objects
        self.config_tables = config_tables

        # A list of tableSpec objects
        self.results_table = results_table


class TableSpec(object):
    """Contains the rendering information for the tables of the
    html report.
    """

    def __init__(self, table_type, title, keys, source_json,
                 ordering_key=None):
        """
        :param table_type: A string describing the type of table that
        we want to generate. It can have one of the following values '1d' for a
        one dimensional table with keys and values, or '2d' for a
        two dimensional table, containing a list of dictionaries. Each
        dictionary contains keys and values of the table fields.
        :param title: The title of the generated table. Put an empty
        string for a table with no title.
        :param keys: Contains a list of tuples that provides a mapping between
        the keys of the json file (that contains the data of the table) and
        the names of the keys that will be printed in the generated html
        report. This parameter also defines the order of the json fields
        inside the generated html table and also which fields will be excluded
        from the report. For '1d' tables the above operations affects the rows
        and for '2d' tables the operations affects the columns. If the value of
        this parameter is None then the field values of the generated html
        table, will be the same as the ones in json file, with the same
        order, defined in this file.
        :param source_json: A string defining the filepath to the json
        file that contains the data of the generated table.
        :param ordering_key: A string value containing the json
        field key, according to which the generated html table will be
        sorted. This value has meaning only for '2d' tables and the
        default value if not defined is None, which means that no sorting
        will be done.
        :type table_type: str
        :type title: str
        :type keys: list<tuple<str>>
        :type source_json: str
        :type ordering_key: str
        """

        self.table_type = table_type
        # convert keys into an OrderedDict object
        if keys is not None:
            self.keys = collections.OrderedDict(keys)
        else:
            self.keys = keys
        self.title = title
        self.source_json = source_json
        self.ordering_key = ordering_key
