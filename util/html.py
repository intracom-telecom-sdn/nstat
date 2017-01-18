# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" HTML generation utilities """

import collections

def generate_html_foot(foot_content=''):
    """Returns the ending and the contents at the end of html page.

    :returns: HTML code of the page ending.
    :rtype: str
    """

    html_foot = '{0}</body></html>'.format(foot_content)
    return html_foot


def generate_html_head(css_style='', javascript_functions='',
                       head_content=''):
    """Creates the head of an html file gets as input the styling of the page \
        as a css string parameter and returns a string value, which is the \
        html code of the header.

    :param css_style: the css styling text of the html page we produce. \
        this parameter must be given as a multiline string.
    :param parameters_dictionary: Parameters of the specific testing scenario
    :param javascript_functions: JavaScript functions for report. This \
        parameter must be given as a multiline string.
    :param head_content: this is the html code that will appear at the top of \
        the page, just after the <body> tag. We can place here the Title of \
        the page and everything else we want to appear at the top.
    :returns: str (the html code of the Header of the html page.)
    :rtype: str
    :type css_style: str
    :type parameters_dictionary: str
    :type javascript_functions: str
    :type head_content: str
    """

    html_head = ('<!DOCTYPE html><html><head>'
                 '<title>Southbound testing</title>'
                 '<meta http-equiv=\"Content-Type\" '
                 'content=\"text/html;charset=UTF-8\"> <style>')
    html_head += css_style + '</style>' + \
    javascript_functions + '</head><body>' + head_content
    return html_head

def get_ordered_index(field_value, map_dictionary):
    """Returns the index of a key in map_dictionary, which is defined by the \
        field_value. If no match is found None is returned

    :param field_value: the value of the key we want to search for, inside \
        the map_dictionary. This is a helper function called inside the
        single_dict_to_html() and multi_dict_to_html() to avoid repetitions of \
        the same code blocks in these functions
    :param map_dictionary: An instance of OrderedDict which has mappings \
        between keys and their values as they appear inside an html generated \
        document.
    :returns: The index where the field_value should be placed, depending on \
        the ordering inside the map_dictionary
    :rtype: int
    :type field_value: str
    :type map_dictionary: collections.OrderedDict
    """

    ordered_index = 0
    for map_key, map_value in list(map_dictionary.items()):
        if map_key == field_value:
            return ordered_index
        else:
            ordered_index = ordered_index + 1
    # In case no match is found, None value is returned as index
    return -1

def isalistofdictionaries(lst):
    """
    Takes a list as argument and checks if all the elements of this list \
        are dictionaries. If they are then it returns true, else it returns \
        false. If the input argument type is not list then it also returns \
        false.

    :param lst: The list that we want to check its elements
    :returns:  True if all the elements of the list are dictionaries. False \
        otherwise
    :rtype: bool
    :type lst: list<dict>
    """

    all_list_items_dict = False
    if isinstance(lst, list):
        if not lst:
            all_list_items_dict = False
        else:
            all_list_items_dict = True
        for list_item in lst:
            if not isinstance(list_item, dict):
                all_list_items_dict = False
                break
    return all_list_items_dict

def multi_dict_to_html(data, table_title='', map_dictionary=None,
                       row_ordering_key=None):
    """Generates html tables according to the input it gets from the input \
        arguments.

    :param data: This datastructure is a list that contains dictionaries of \
        strings that contains the pair of field_name:value of all the data we \
        want to convert to HTML table.
    :param table_title: An optional argument that contains the title of the \
        table we want to generate.
    :param map_dictionary: data structure that contains the pair of \
        field_name:value. It defines which fields will be kept from the data \
        input dictionary and how their value will be translated in the HTML \
        table.
    :returns: str
    :rtype: str
    :type data: list<dict>
    :type table_title: str
    :type map_dictionary: controller.OrderedDict
    """

    if map_dictionary is None:
        col_size = len(data[0])
    else:
        col_size = len(map_dictionary)
    if row_ordering_key is not None:
        data = sorted(data, key=lambda k: k[row_ordering_key])
    table_html = '<table class=\"tableWithFloatingHeader\">'
    table_html = table_html + '<thead>'
    if table_title != '':
        table_html = table_html + '<tr><th colspan=\"' + str(col_size) + \
            '\" class=\"table-title\">' + str(table_title) + '</th></tr>'
    table_html = table_html + '<tr>'
    if map_dictionary is None:
        for field_value, data_value in list(data[0].items()):
            table_html = table_html + '<th>' + str(field_value) + '</th>'
    else:
        for field_key, field_value in list(map_dictionary.items()):
            if field_key in data[0]:
                table_html = table_html + '<th>' + str(field_value) + '</th>'
            else:
                # Remove from map dictionary entries that do not exist inside
                # the data in order not to affect the rest of the process
                del map_dictionary[field_key]
    table_html = table_html + '</tr></thead>'
    table_html = table_html + '<tbody>'
    num_row = 0
    for data_row in data:
        if num_row % 2 == 0:
            table_html = table_html + '<tr>'
        else:
            table_html = table_html + '<tr class=\"odd\">'
        ordered_row = collections.OrderedDict()
        for field_value, data_value in list(data_row.items()):
            ordered_row_index = 0
            if map_dictionary is None:
                table_html = table_html + '<td>' + str(data_value) + '</td>'
            elif field_value in map_dictionary:
                ordered_row_index = get_ordered_index(field_value,
                                                      map_dictionary)
                ordered_row[ordered_row_index] = '<td>' + \
                    str(data_value) + '</td>'

        for row_key in sorted(ordered_row.keys()):
            table_html = table_html + ordered_row[row_key]
        table_html = table_html + '</tr>'
        num_row += 1
    table_html = table_html + '</tbody>'
    table_html = table_html + '</table>'
    return str(table_html)

def single_dict_table_data(data_values, td_style=None, td_class=None):
    """
    Returns a <td> ... </td> html element for the single_dict_to_html() \
        type of tables, data columns. In case that the input data_values is a \
        list of dictionaries, this function calls recursively \
        single_dict_to_html() and generates sub tables inside the \
        <td> ... </td> html element.

    :param data_values: the data we want to place into a <td> ... </td> html \
        element.
    :param td_style: the styling code for the content of <td>...</td> html \
        element.
    :param cls: the class name attribute of the <td>...</td> html element
    :returns: html code of a <td>  </td> element for single_dict_to_html()
        tables
    :rtype: str
    :type style: str
    :type cls: str
    :type data_values: str or list<dict>
    """

    cell_str = '<td'
    if td_style:
        cell_str += ' style=\"' + td_style + '\"'
    if td_class:
        cell_str += ' class=\"' + td_class + '\"'
    cell_str += '>'
    if isalistofdictionaries(data_values) == True:
        # In case we have a list of dictionaries recursive call
        # of function
        for data_value in data_values:
            cell_str += single_dict_to_html(data_value, '', '', '', None)
        cell_str += '</td>'
    else:
        cell_str += str(data_values) + '</td>'
    return cell_str

def single_dict_to_html(data, key_title, data_title, table_title='',
                        map_dictionary=None):
    """
    Generates html tables according to the input it gets from the input \
        arguments. The table generated is by row, which means that on each row \
        the first element is the key value of the dictionary, the second \
        element is the data value of the dictionary for the correspondent key. \
        The columns are always 2 and their title are defined in the input \
        arguments

    :param data: this data structure is a dictionary of strings that contains \
        the pair of field_name:value for all the data we want to convert to \
        HTML table.
    :param key_title: the title of the column, under which the dictionary key \
        values will be placed.
    :param data_title: the title of the column, under which the dictionary \
        data values will be placed.
    :param table_title: Optional argument. Contains the title of the table we \
        want to generate
    :param map_dictionary: This data structure contains the pair of \
        field_name:value. It defines which fields should be kept from the data \
        input dictionary and how their value will be translated in the HTML \
        table.
    :returns: str
    :rtype: str
    :type data: dict
    :type key_title: str
    :type data_title: str
    :type table_tytle:str
    :type map_dictionary: collections.OrderedDict
    """

    table_html = '<table class=\"tableWithFloatingHeader\">'
    table_html = table_html + '<thead>'
    if table_title != '':
        table_html = table_html+'<tr><th class=\"table-title\" colspan=\"2\">' + \
            str(table_title) + '</th></tr>'
    table_html = table_html + '<tr>'
    table_html = table_html + '<th>' + str(key_title) + '</th>'
    table_html = table_html + '<th>' + str(data_title) + '</th>'
    table_html = table_html + '</tr></thead>'
    table_html = table_html + '<tbody>'
    row_ordered = collections.OrderedDict()
    row_ordered_index = 0
    for field_value, data_value in list(data.items()):
        row_str = ''
        if map_dictionary is None:
            if row_ordered_index % 2 == 0:
                row_str = row_str + '<tr>'
            else:
                row_str = row_str + '<tr class=\"odd\">'
            single_dict_table_data(data_values=str(field_value),
                                   td_style='font-weight:bold;')
            # If other List of dictionaries exist then we call recursively
            # the function to generate subtables inside the columns of
            # the main table. Else we just place the data_value inside the
            # cell of the table
            row_str = row_str + single_dict_table_data(data_value)
            row_str = row_str + '</tr>'
            row_ordered[row_ordered_index] = row_str
            row_ordered_index = row_ordered_index + 1
        elif field_value in map_dictionary:
            row_ordered_index = get_ordered_index(field_value,
                                                  map_dictionary)
            if row_ordered_index % 2 == 0:
                row_str = row_str + '<tr>'
            else:
                row_str = row_str + '<tr class=\"odd\">'
            row_str = row_str + '<td style=\"font-weight:bold;\">' + \
            str(map_dictionary[field_value]) + '</td>'
            # If other List of dictionaries exist then we call recursively
            # the function to generate sub tables inside the columns of
            # the main table. Else we just place the data_value inside the
            # cell of the table
            row_str = row_str + single_dict_table_data(data_value)
            row_str = row_str + '</tr>'
            row_ordered[row_ordered_index] = row_str
            row_ordered_index = 0
    for row_key in sorted(row_ordered.keys()):
        table_html = table_html+row_ordered[row_key]
    table_html = table_html + '</tbody>'
    table_html = table_html + '</table>'
    return str(table_html)