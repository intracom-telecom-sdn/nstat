# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" HTML generation functions """
import json
import optparse
import report_spec
import util.html


def generate_html(report_spec, report_filename):
    """
    Generates the test HTML report

    :param report_spec: report specification for this report
    :param report_filename: target HTML filename
    :type report_spec: ReportSpec
    :type report_filename: str
    """

    # The following multiline variable contains Javascript functions
    # that are integrated into the html report. The specific ones make the
    # headers of tables scroll with the page

    javascript_functions = '''
<script type="text/javascript"
src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js">
</script>
<script type="text/javascript">
//<![CDATA[
/**
 * Usage: Call ActivateFloatingHeader with a CSS selector(string) matching
 *        table elements that should have a floating header
 *
 *  $(document).ready(function() {
 *      ActivateFloatingHeaders("table.tableWithFloatingHeader");
 *  });
 */


function _UpdateTableHeadersScroll() {
    $("div.divTableWithFloatingHeader").each(function() {
        var originalHeaderRow = $(".tableFloatingHeaderOriginal", this);
        var floatingHeaderRow = $(".tableFloatingHeader", this);
        var offset = $(this).offset();
        var scrollTop = $(window).scrollTop();
        // check if floating header should be displayed
        if ((scrollTop > offset.top) &&
            (scrollTop <
             offset.top + $(this).height() - originalHeaderRow.height())) {
            floatingHeaderRow.css("visibility", "visible");
            floatingHeaderRow.css("left", -$(window).scrollLeft());
        }
        else {
            floatingHeaderRow.css("visibility", "hidden");
        }
    });
}


function _UpdateTableHeadersResize() {
    $("div.divTableWithFloatingHeader").each(function() {
        var originalHeaderRow = $(".tableFloatingHeaderOriginal", this);
        var floatingHeaderRow = $(".tableFloatingHeader", this);

        // Copy cell widths from original header
        $("th", floatingHeaderRow).each(function(index) {
            var cellWidth = $("th", originalHeaderRow).eq(index).css('width');
            $(this).css('width', cellWidth);
        });

        // Copy row width from whole table
        floatingHeaderRow.css("width", Math.max(originalHeaderRow.width(),
                              $(this).width()) + "px");

    });
}


function ActivateFloatingHeaders(selector_str){
    $(selector_str).each(function() {
        $(this).wrap('<div class="divTableWithFloatingHeader" ' +
                     'style="position:relative"></div>');

        // use first row as floating header by default
        var floatingHeaderSelector = "thead";
        var explicitFloatingHeaderSelector = "thead.floating-header"
        if ($(explicitFloatingHeaderSelector, this).length){
            floatingHeaderSelector = explicitFloatingHeaderSelector;
        }

        var originalHeaderRow = $(floatingHeaderSelector, this).first();
        var clonedHeaderRow = originalHeaderRow.clone()
        originalHeaderRow.before(clonedHeaderRow);

        clonedHeaderRow.addClass("tableFloatingHeader");
        clonedHeaderRow.css("position", "fixed");
        // not sure why but 0px is used there is still some space in the top
        clonedHeaderRow.css("top", "-2px");
        clonedHeaderRow.css("margin-left", $(this).offset().left+1);
        clonedHeaderRow.css("margin-right", $(this).offset().right+1);
        clonedHeaderRow.css("visibility", "hidden");

        originalHeaderRow.addClass("tableFloatingHeaderOriginal");
    });
    _UpdateTableHeadersResize();
    _UpdateTableHeadersScroll();
    $(window).scroll(_UpdateTableHeadersScroll);
    $(window).resize(_UpdateTableHeadersResize);
}
//]]>
</script>
<script type="text/javascript">
//<![CDATA[
    $(document).ready(function() {
        ActivateFloatingHeaders("table.tableWithFloatingHeader");
});
//]]>
</script>
'''
    # In the following multiline variable, we keep the information about the
    # formating of the produced html document as a css string.
    default_css_styling = '''
body {
margin:0;
padding:20px;
font:13px "Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, sans-serif;
}

/* ---- Resets ---- */

p, table, caption, td, tr, th {
    margin:0;
    padding:0;
    font-weight:normal;
    }

/* ---- Paragraphs ---- */

p {
    margin-bottom:15px;
    }

/* ---- Table ---- */

table {
    border-collapse:separate;
    border-spacing:0px;
    margin-bottom:15px;
    width:90%;
    border:1px solid #cccccc;
    }

    caption {
        text-align:left;
        font-size:15px;
        padding-bottom:10px;
        }

    table td,
    table th {
        padding:5px;
        border:1px solid #fff;
        border-width:0px 1px 1px 0px;
        vertical-align: middle;
        }

    thead th {
        background:#91c5d4;
        font-size: 17px;
        font-weight:bold;
        text-align:center;
        }

    thead th.table-title {
        font-size:19px;
        font-weight:bold;
        text-align:left;
        }

    thead th[colspan],
    thead th[rowspan] {
        background:#66a9bd;
        }

    tbody th,
    tfoot th {
        text-align:left;
        background:#91c5d4;
        }

    tbody td,
    tfoot td {
        text-align:left;
        background:#d5eaf0;
        font-size:16px;
        font-weight:normal;
        }

    tbody td.center {
        text-align:center;
        }

    tfoot th {
        background:#b0cc7f;
        }

    fieldset {
        width:30%;
        font-size:16px;
        border: 1px solid #000000;
        padding: 10px;
        }

    fieldset.left {
        float:left;
        margin-right:20px;
        }

    fieldset legend {
        font-size:17px;
        font-weight:bold;
        }

    tfoot td {
        background:#d7e1c5;
        font-weight:bold;
        }

    tbody tr.odd td {
        background:#bcd9e1;
        }

    img {
        width:49%;
        max-width:800px;
        min-width:640px;
        height:auto;
        border: 0;
    }

    img.graph-left{
        float:left;
        margin-right:1px;
    }

    img.graph-right{
        float:right;
        margin-left:1px;
    }

    div.graph-container{
        float:left;
        width:100%;
        max-width:1605px;
        min-width:1285px;
    }

    div.float-cleaner{
        clear:both;
    }
'''

    content = ''
    params = json.loads(open(report_spec.config_json).read())

    # The content on the top of the html report
    html_head_content = '<h1>' + report_spec.title + '</h1><hr>'

    # Generating header of the report page
    content = content + util.html.generate_html_head(default_css_styling,
                                                     javascript_functions,
                                                     html_head_content)

    # Generating results parameters table
    content = content + generate_table(report_spec.config_tables)

    # Inserting plots inside the report page
    content = content +insert_plots(params['plots'])

    # Generating test results table
    content = content + generate_table(report_spec.results_table)

    content = content + util.html.generate_html_foot()
    repf = open(report_filename, 'w')
    repf.write(content)
    repf.close()

def generate_table(tables_specs):
    """ Gets a dictionary with tables specifications and generates the
    corresponded html code.

    :param tables_specs: Dictionary containing the specifications of a group
    of tables.
    :returns: html code of the table.
    :rtype: str
    :type tables_specs: <dictionary>
    """

    table_html = ''
    for table_specs in tables_specs:
        table_data = json.loads(open(table_specs.source_json).read())
        if table_specs.table_type == '1d':
            table_html = table_html + \
                util.html.single_dict_to_html(table_data, 'Parameter', 'Value',
                    table_specs.title, table_specs.keys)
        elif table_specs.table_type == '2d':
            table_html = table_html + \
                util.html.multi_dict_to_html(table_data, table_specs.title,
                    table_specs.keys, table_specs.ordering_key)
        table_html = table_html + '<br>' + '<hr>'
    return table_html


def insert_plots(plots_list):
    """ Gets a list of dictionaries that describes the plots of the report,
    and generates the corresponded html code.

    :param plots_list: A list of dictionaries with the plots description.
    :returns: The corresponded html code to insert the plots.
    :rtype: str
    :type plots_list: <list<dictionary>>
    """

    num_plots = len(plots_list)
    plots_html = ''
    if num_plots:
        plots_html = plots_html + '<div class=\"graph-container\">'
        graph_float = 'left'

        for plot_id in list(range(0, num_plots)):
            if plots_list[plot_id]['plot_filename']:

                # Adding a graph image in document.
                plots_html = plots_html + \
                    '<img class=\"graph-' + graph_float + '\" src=\"' + \
                str(plots_list[plot_id]['plot_filename']) + \
                    '.png\" alt=\"result graph\" />'

                # Changing the page alignment of the next inserted graph image.
                # Also place a content break to have images group of 2.
                if graph_float == 'right':
                    plots_html = plots_html + \
                        '<div class=\"float-cleaner\"><br></div>'
                    graph_float = 'left'
                else:
                    graph_float = 'right'

        plots_html = plots_html + '</div>'
        plots_html = plots_html + '<div class=\"float-cleaner\"><br></div>'

    plots_html = plots_html + '<hr>'
    return plots_html


def self_test():
    """
    Used for self testing purposes
    """
    opt_parser = optparse.OptionParser()

    opt_parser.add_option('--input-results', dest='RESULTS_JSON',
                          action='store', default='results.json',
                          help="pathname of the result json file to open")
    opt_parser.add_option('--input-conf', dest='PARAMETERS_JSON',
                          action='store', default='conf.json',
                          help='name of the parameter json file to open')
    opt_parser.add_option('--html-report', dest='report_filename',
                          action='store', default='report.html',
                          help='name of the filename of html report')
    (json_opts, args_remainder) = opt_parser.parse_args()
    report_test = report_spec.ReportSpec(json_opts.PARAMETERS_JSON,
                      json_opts.RESULTS_JSON, 'test',
                          [report_spec.TableSpec('1d', 'config',
                              [('controller_start', 'Controller Start'),
                               ('controller_stop', 'Controller Stop'),
                               ('java_opts', 'Java Options')
                              ],json_opts.PARAMETERS_JSON)
                           ],
                           [report_spec.TableSpec('2d', 'results', None,
                                json_opts.RESULTS_JSON,
                                'generator_thread_creation_delay_ms')
                           ]
                      )
    generate_html(report_test, json_opts.report_filename)

# Used for self-testing purposes.
if __name__ == '__main__':
    self_test()

