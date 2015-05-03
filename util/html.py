# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" HTML generation utilities """

import collections as c


def generate_html_foot(foot_content = ''):
    """Returns the ending of html page.
    :returns: HTML code of the page ending."""
    html_foot = '</body></html>{0}'.format(foot_content)
    return html_foot


def generate_html_head(css_style = '', javascript_functions = '', 
                       head_content = ''):
    """Creates the head of an html file gets as input the
        styling of the page as a css string parameter and returns a string
        value, which is the html code of the header.
    :param css_style: The css styling text of the html page we produce
    :param parameters_dictionary: Parameters of the
        specific testing scenario
    :param javascript_functions: Javascript functions for report
        presentation enhancement.
    :returns: The html code of the Header of the html page
    """

    html_head = '<html><head><title>Southbound testing</title>\
    <meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\">\
    <meta charset=\"UTF-8\"><style>' + css_style + '</style>' + \
    javascript_functions + '</head>' + head_content
    return html_head

def is_a_list_of_dictionaries(l):
    """
    Takes a list as argument and checks if all the elements
    of this list are dictionaries. If they are then it returns true, else it
    returns false. If the input argument type is not list then it also returns
    false.
    :param l: The list that we want to check its elements
    :returns:  True: if all the elements of the list are dictionaries
               False: otherwise
    """
    all_list_items_dict = False
    if type(l) == type([]):
        if not l:
            all_list_items_dict = False
        else:
            all_list_items_dict = True
        for d in l:
            if type(d) != type({}):
                all_list_items_dict = False
                break
    return all_list_items_dict

def multy_dict_to_html(data, table_title = '', map_dictionary = None):
    """
    Generates html tables according to the input it gets
    from the input arguments.
    :param data: This datastructure is a list that contains
            dictionaries of strings that contains the pair of
            field_name:value of all the data we want to convert to HTML table
    :param table_title: An optional argument that
            contains the title of the table we want to generate
    :param map_dictionary: Datastructure that contains the
            pair of field_name:value. It defines which fields will be kept
            from the data input dictionary and how their value will be
            translated in the HTML table
    :returns: The HTML code of the table
    """
    # TODO - validate the data input parameter. Enhancement
    if map_dictionary is None:
        col_size = len(data[0])
    else:
        col_size = len(map_dictionary)

    table_html = '<table border=\"1\" cellpadding=\"3\" cellspacing=\"0\"' + \
    ' class=\"tableWithFloatingHeader\">'
    table_html = table_html + '<thead>'
    if table_title != '':
        table_html = table_html + \
        '<tr><th colspan=\"' + str(col_size) + '\" class=\"title\">' + \
        str(table_title) + \
        '</th></tr>'
    table_html = table_html + '<tr>'
    if map_dictionary is None:
        for (field_value, data_value) in data[0].iteritems():
            table_html = table_html + '<th>' + str(field_value) + '</th>'
    else:
        for (k, field_value) in map_dictionary.iteritems():
            if k in data[0]:
                table_html = table_html + '<th>' + str(field_value) + '</th>'
            else:
                # Remove from map dictionary entries that do not exist inside
                # the data in order not to affect the rest of the process
                del map_dictionary[k]

    table_html = table_html + '</tr></thead>'
    table_html = table_html + '<tbody>'
    num_row = 0
    for data_row in data:
        if (num_row % 2) == 0:
            table_html = table_html + '<tr>'
        else:
            table_html = table_html + '<tr class=\"odd\">'
        ordered_row = c.OrderedDict()
        for (field_value, data_value) in data_row.iteritems():
            ordered_row_index = 0
            if map_dictionary is None:
                table_html = table_html + '<td>' + str(data_value) + '</td>'
            else:
                if field_value in map_dictionary:
                    for k, v in map_dictionary.iteritems():
                        if k == field_value:
                            break
                        else:
                            ordered_row_index = ordered_row_index+1
                    ordered_row[ordered_row_index] = '<td>' + \
                    str(data_value) + \
                    '</td>'
        for i in sorted(ordered_row.keys()):
            table_html = table_html + ordered_row[i]
        table_html = table_html + '</tr>'
        num_row += 1
    table_html = table_html + '</tbody>'
    table_html = table_html + '</table>'
    return str(table_html)

def single_dict_to_html(data, key_title, data_title, table_title, 
                        map_dictionary):
    """
    Generates html tables according to the input it gets
    from the input arguments. The table generated is by row, which means that
    on each row the first element is the key value of the dictionary, the 
    second element is the data value of the dictionary for the correspondent 
    key. The columns are always 2 and their title are defined in the input 
    arguments
    :param data: This datastructure is a dictionary of strings
            that contains the pair of field_name:value for all the data
            we want to convert to HTML table
    :param key_title: The title of the column, under which the
            dictionary key values will be placed.
    :param data_title: The title of the column, under which the
            dictionary data values will be placed.
    :param table_title: Optional argument.
            Contains the title of the table we want to generate
    :param map_dictionary: This datastructure contains the
            pair of field_name:value. It defines which fields will be kept
            from the data input dictionary and how their value will be
            translated in the HTML table
    :returns: The HTML code of the table
    """
    # TODO - validate the data input parameter. Probably do this by creating
    # a new function that will return true or false depending on weather data
    # is valid or not
    if map_dictionary is None:
        col_size = len(data)
    else:
        col_size = len(map_dictionary)

    table_html = '<table border=\"1\" cellpadding=\"3\" cellspacing=\"0\"' + \
    'class=\"tableWithFloatingHeader\">'
    table_html = table_html + '<thead>'
    if table_title != "":
        table_html = table_html+'<tr><th class=\"title\" colspan=\"' + \
        str(col_size) + '\">' + str(table_title) + '</th></tr>'
    table_html = table_html + '<tr>'
    table_html = table_html + '<th>' + str(key_title) + '</th>'
    table_html = table_html + '<th>' + str(data_title) + '</th>'
    table_html = table_html + '</tr></thead>'
    table_html = table_html + '<tbody>'
    row_ordered = c.OrderedDict()
    row_ordered_index = 0
    for (field_value, data_value) in data.iteritems():
        row_str = ''
        if map_dictionary is None:
            if (row_ordered_index % 2) == 0:
                row_str = row_str + '<tr>'
            else:
                row_str = row_str + '<tr class=\"odd\">'
            row_str = row_str + '<td style=\"font-weight:bold;\">' + \
            str(field_value) + '</td>'
            if is_a_list_of_dictionaries(data_value) == True:
                # In case we have a list of dictionaries recursive call
                # of function
                row_str = row_str + '<td>'
                for d in data_value:
                    row_str = row_str + \
                    single_dict_to_html(d, '', '', '', None)
                row_str = row_str + '</td>'
            else:
                row_str = row_str + '<td>' + str(data_value) + '</td>'
            row_str = row_str + '</tr>'
            row_ordered[row_ordered_index] = row_str
            row_ordered_index = row_ordered_index + 1
        else:
            if field_value in map_dictionary:
                for k, v in map_dictionary.iteritems():
                    if k == field_value:
                        break
                    else:
                        row_ordered_index = row_ordered_index + 1
                if (row_ordered_index % 2) == 0:
                    row_str = row_str + '<tr>'
                else:
                    row_str = row_str + '<tr class=\"odd\">'
                row_str = row_str + '<td style=\"font-weight:bold;\">' + \
                str(map_dictionary[field_value]) + '</td>'

                if is_a_list_of_dictionaries(data_value) == True:
                    # In case we have a list of dictionaries recursive call
                    # of function
                    row_str = row_str + '<td>'
                    for d in data_value:
                        row_str = row_str + \
                        single_dict_to_html(d, '','','', None)
                    row_str = row_str + '</td>'
                else:
                    row_str = row_str + '<td>' + str(data_value) + '</td>'
                row_str = row_str + '</tr>'
                row_ordered[row_ordered_index] = row_str
                row_ordered_index = 0

    for i in sorted(row_ordered.keys()):
        table_html = table_html+row_ordered[i]
    table_html = table_html + '</tbody>'
    table_html = table_html + '</table>'
    return str(table_html)
