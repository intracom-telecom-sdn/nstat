# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
# 
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Here the HTML report is generated """

import json
import optparse
import collections as c
import util.html as html_util


def generate_html(parameters_json, results_json, 
                  report_filename, test_type = ''):
    """
    Generates the HTML report of the performance test.
    :param parameters_json: The json file with the test parameters
    :param results_json: The json file with the test results
    :param report_filename: This is the target HTML file which is 
           going to be generated
    :param test_type: A string value describing the type of the test that 
           was run
    """
    # The following multiline, variable contains useful javascript functions 
    # that are integrated into the html report. The specific ones make the 
    # headers of tables scroll with the page
    javascript_functions = '''
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
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
        if ((scrollTop > offset.top) && (scrollTop < offset.top + $(this).height() - originalHeaderRow.height())) {
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
        floatingHeaderRow.css("width", Math.max(originalHeaderRow.width(), $(this).width()) + "px");

    });
}


function ActivateFloatingHeaders(selector_str){
    $(selector_str).each(function() {
        $(this).wrap("<div class=\\"divTableWithFloatingHeader\\" style=\\"position:relative\\"></div>");

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
        clonedHeaderRow.css("margin-left", $(this).offset().left);
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

p,
table, caption, td, tr, th {
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
    margin-bottom:15px;
    width:90%;
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

    thead th.title {
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
'''

    # This is the dictionary that renames , orders and selects the json fields 
    # of the result data, that are included inside the html table
    json_test_data_fields = c.OrderedDict()
    json_test_data_fields['global_sample_id'] = 'Sample ID'
    json_test_data_fields['timestamp'] = 'Sample timestamp (seconds)'
    json_test_data_fields['date'] = 'Sample timestamp (date)'
    json_test_data_fields['test_repeats'] = 'Total test repeats'
    json_test_data_fields['repeat_id'] = 'External repeat ID'
    json_test_data_fields['generator_internal_repeats'] = ('Generator'
                                                           ' Internal repeats')
    json_test_data_fields['bootup_time_secs'] = ('Time to discover '
                                                 'switches (seconds)')
    json_test_data_fields['discovered_switches'] = 'Discovered switches'
    json_test_data_fields['internal_repeat_id'] = 'Internal repeat ID'
    json_test_data_fields['throughput_responses_sec'] = ('Throughput'
                                                         ' (responces/sec)')
    json_test_data_fields['generator_simulated_hosts'] = ('Generator '
                                                          'simulated hosts')
    json_test_data_fields['generator_switches'] = ('Generated simulated'
                                                   ' switches')
    json_test_data_fields['generator_threads'] = 'Generator threads'
    json_test_data_fields['generator_switches_per_thread'] = ('Switches per '
                                                            'generator thread')
    json_test_data_fields['generator_thread_creation_delay_ms'] = ('Generator'
                                    ' delay before traffic transmission (ms)')
    json_test_data_fields['generator_delay_before_traffic_ms'] = ('Delay '
                                            'between switches requests (ms)')
    json_test_data_fields['generator_ms_per_test'] = ('Internal repeats'
                                                      ' interval')
    json_test_data_fields['generator_warmup'] = 'Generator warmup repeats'
    json_test_data_fields['generator_mode'] = 'Generator test mode'
    json_test_data_fields['controller_ip'] = 'Controller IP'
    json_test_data_fields['controller_port'] = 'Controller port'
    json_test_data_fields['controller_restart'] = 'Restart controller'
    json_test_data_fields['controller_java_xopts'] = 'Java options'
    json_test_data_fields['one_minute_load'] = 'One minute load'
    json_test_data_fields['five_minute_load'] = 'five minutes load'
    json_test_data_fields['fifteen_minute_load'] = 'fifteen minutes load'
    json_test_data_fields['used_memory_bytes'] = 'System used memory (Bytes)'
    #json_test_data_fields['free_memory_bytes'] = 'System free memory (Bytes)'
    json_test_data_fields['total_memory_bytes'] = 'Total system memory'
    json_test_data_fields['controller_cpu_system_time'] = ('Controller '
                                                           'CPU system time')
    json_test_data_fields['controller_cpu_user_time'] = ('Controller CPU '
                                                         'user time')
    json_test_data_fields['controller_num_threads'] = 'Controller threads'
    json_test_data_fields['controller_num_fds'] = 'Controller num of fds'
    #json_test_data_fields['iowait_time'] = 'I/O wait time'
    #json_test_data_fields['controller_vm_size'] = 'Controller VM size (Bytes)'
    #json_test_data_fields['controller_cwd'] = 'Controller working dir'
    
    # If you want to print all the test results with their original json 
    # names and order, comment out the following line.
    #json_test_data_fields=None


    # This is the dictionary that renames orders and selects the json fields 
    # of the parameters data, that are included inside the html table
    json_test_parameters_fields = c.OrderedDict()
    json_test_parameters_fields['test_repeats'] = 'Test repeats'
    json_test_parameters_fields['controller_name'] = 'Controller name'
    json_test_parameters_fields['controller_build'] = 'Controller build script'
    json_test_parameters_fields['controller_start'] = 'Controller start script'
    json_test_parameters_fields['controller_stop'] = 'Controller stop script'
    json_test_parameters_fields['controller_status'] = ('Controller'
                                                        ' status script')
    json_test_parameters_fields['controller_clean'] = ('Controller '
                                                       'cleanup script')
    json_test_parameters_fields['controller_ip'] = 'Controller IP address'
    json_test_parameters_fields['controller_port'] = ('Controller'
                                                      ' listening port')
    json_test_parameters_fields['controller_restart'] = ('Controller restart'
                                                    ' between test repeats')
    json_test_parameters_fields['controller_rebuild'] = ('Controller rebuild'
                                                    ' between test repeats')
    json_test_parameters_fields['controller_logs_dir'] = ('Controller log'
                                                          ' save directory')

    json_test_parameters_fields['generator_name'] = 'Generator name'
    json_test_parameters_fields['generator_build'] = 'Generator build script'
    json_test_parameters_fields['generator_run'] = 'Generator start script'
    json_test_parameters_fields['generator_clean'] = 'Generator cleanup script'
    json_test_parameters_fields['generator_simulated_hosts'] = ('Generator'
                                                            ' simulated hosts')
    json_test_parameters_fields['generator_threads'] = 'Generator threads'
    json_test_parameters_fields['generator_thread_creation_delay_ms'] = (
                'Generation delay in ms between thread creation')
    json_test_parameters_fields['generator_switches_per_thread'] = ('Switches'
                                                    ' per generator thread')
    json_test_parameters_fields['generator_internal_repeats'] = ('Generator'
                                                        ' internal repeats')
    json_test_parameters_fields['generator_ms_per_test'] = ('Internal '
                                                    'repeats duration in ms')
    json_test_parameters_fields['generator_rebuild'] = ('Generator rebuild'
                                                ' between each test repeat')
    json_test_parameters_fields['generator_mode'] = 'Generator testing mode'
    json_test_parameters_fields['generator_warmup'] = ('Generator warmup'
                                                       ' repeats')
    json_test_parameters_fields['generator_delay_before_traffic_ms'] = (
                                'Generator delay before sending trafic in ms')
    json_test_parameters_fields['java_opts'] = ('JVM options')
    # If you want to print all the test parameters with their original json 
    # names and order, comment out the following line.
    #json_test_parameters_fields=None

    content = ''
    params = json.loads(open(parameters_json).read())
    results = json.loads(open(results_json).read())
    
    # Get the controller_cwd from report file
    try:
        if str(results[0]['controller_cwd']).replace(' ', ''):
            controller_cwd = str(results[0]['controller_cwd']).replace(' ', '')
        else:
            controller_cwd = 'Not available. Empty value'
    except:
        controller_cwd = 'Does not exist in results report json file'
    
    # The content on the top of the html report
    html_head_content = '<body><h1>Southbound Performance Testing</h1>' + \
              '<fieldset class=\"left\">' + \
              '<legend> Test setup parameters </legend>' + \
              '<p>Test type: ' + str(test_type) + '</p>' + \
              '<p>Controller: ' + str(params['controller_name']) + '</p>' + \
              '<p>Controller working dir: ' + str(controller_cwd) + '</p>' + \
              '</fieldset> ' + \
              '<fieldset> ' + \
              '<legend> Generator parameters </legend>' + \
              '<p>#Generator threads: ' + str(params['generator_threads']) + \
              '</p>' + \
              '<p>#Switches per generator thread: ' + \
               str(params['generator_switches_per_thread']) + '</p>' + \
              '<p>Thread creation delay (ms): ' + \
               str(params['generator_thread_creation_delay_ms']) + '</p>' + \
              '<p>Delay before traffic (ms): ' + \
              str(params['generator_delay_before_traffic_ms']) + '</p>' + \
              '<p>Test duration (ms): ' + \
              str(params['generator_ms_per_test']) + '</p>' + \
              '<p>#Internal repeats: ' + \
              str(params['generator_internal_repeats']) + '</p>' + \
              '<p>#Hosts: ' + \
              str(params['generator_simulated_hosts']) + '</p>' + \
              '<p>Generator: ' + str(params['generator_name']) + '</p>' + \
              '</fieldset>' + \
              '<hr />'
    # Generating header of the report page
    content = content + html_util.generate_html_head(default_css_styling, 
                                                    javascript_functions, 
                                                    html_head_content)
    # Generating results parameters table table
    content = content + \
    html_util.single_dict_to_html(params, 'Parameter Name', 'Parameter Value', 
                        'Test configuration parameters (detailed)', 
                        json_test_parameters_fields)
    # Generating inserting graph inside the report page
    num_plots = len(params['plots'])
    if num_plots :
        for i in range(0, num_plots):
            if params['plots'][i]['plot_filename'] :
                content = content + '<br clear=\"all\" />' + \
                '<hr />' + \
                '<img src=\"' + str(params['plots'][i]['plot_filename']) + \
                '.png' + '\" border=\"0\" alt=\"result graph\" />'
                content = content + '<br clear=\"all\" />' + \
                '<hr />'
    # Generating test results table
    content = content + html_util.multy_dict_to_html(results, 
                                           'Test results', 
                                           json_test_data_fields)
    content = content + html_util.generate_html_foot()
    f = open(report_filename, 'w')
    f.write(content)
    f.close()

# This is used for unit-testing purposes.
if __name__ == '__main__':
    option_parser = optparse.OptionParser()

    option_parser.add_option('--input-results', dest = 'RESULTS_JSON', 
                      action = 'store', default = 'results.json', 
                      help = "pathname of the result json file to open")
    option_parser.add_option('--input-conf', dest = 'PARAMETERS_JSON', 
                      action = 'store', default = 'conf.json', 
                      help = 'name of the parameter json file to open')
    option_parser.add_option('--input-filename', dest = 'report_filename', 
                      action='store', default = 'report.html', 
                      help = 'name of the filename of html report')
    (opts, args_remainder) = option_parser.parse_args()
    generate_html(opts.PARAMETERS_JSON, opts.RESULTS_JSON, 
                  opts.report_filename, 'Active test')

