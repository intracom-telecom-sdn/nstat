# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

"""Unittest Module for util/html.py."""

import unittest
import util.html
import collections

class HtmlGenerateHtmlFoot(unittest.TestCase):
    """Unittest class that tests the different functionalities of
    generate_html_foot() method in module util/html.py.
    """

    def setUp(self):
        """Initializes the testing environment parameters for the
        Unittest class htmlGenerateHtmlFoot.
        """

        self.foot_output = '<p>testing</p></body></html>'
        self.foot_input = '<p>testing</p>'

    def test01_generate_html_foot(self):
        """Checks the generate_html_footl() method of util/html.py.
        It checks the equality of the result of an input.
        """

        self.assertMultiLineEqual(self.foot_output,
                                  util.html.
                                  generate_html_foot(self.foot_input),
                                  'Testing generate_foot output')

    def tearDown(self):
        """Cleans the testing environment parameters for the Unittest
        class htmlGenerateHtmlFoot
        """

        del self.foot_output
        del self.foot_input

class HtmlGenerateHead(unittest.TestCase):
    """Unittest class that tests the different functionalities of
    generate_html_head() method in module util/html.py.
    """

    def setUp(self):
        """Initializes the testing environment parameters for for the
        Unittest class htmlGenerateHead
        """

        self.head_output = ('<!DOCTYPE html><html><head>'
                            '<title>Southbound testing</title>'
                            '<meta http-equiv="Content-Type" '
                            'content="text/html;charset=UTF-8"> '
                            '<style><!--- Here goes CSS --></style>'
                            '<!-- Here goes JavaScript --></head><body>'
                            '<!-- Here goes Header content -->')
        self.head_input = ('<!--- Here goes CSS -->',
                           '<!-- Here goes JavaScript -->',
                           '<!-- Here goes Header content -->')

    def test01_generate_html_head(self):
        """Checks the generate_html_headl() method of util/html.py.
        It checks the equality of the result of an input.
        """

        self.assertMultiLineEqual(self.head_output,
                                  util.html.
                                  generate_html_head(*self.head_input),
                                  'Testing generate_head output')

    def tearDown(self):
        """Cleans the testing environment parameters for for the
        Unittest class htmlGenerateHead
        """

        del self.head_input
        del self.head_output

class HtmlIsAListOfDictionaries(unittest.TestCase):
    """Unittest class that tests the different functionalities of the
    isalistofdictionaries() function in module util/html.py.
    The investigated cases are the following
    - Case that the input is a list of dictionaries
    - Case that the input is a list that its elements are not dictionaries
    - Case that the input is not a list at all
    """

    @classmethod
    def setUpClass(cls):
        """Initializes the testing environment parameters
        """

        cls.list_of_dictionaries = [{'a':1, 'b':2, 'f':5}, {'c':3, 'd':4}]
        cls.not_list_of_dictionaries = [1, 2, 'a', 3]
        cls.noise = 'This_is_just_noise'

    def test01_isalistofdictionaries(self):
        """Checks the isalistofdictionaries() method of
        util/html.py. It checks the equality of the result of an input.
        - in this case is checked the result, when the provided input is a
        list of dictionaries
        """

        self.assertTrue(util.html.
                        isalistofdictionaries(self.list_of_dictionaries),
                        ('Testing isalistofdictionaries output. '
                         'Assert true'))

    def test02_isalistofdictionaries(self):
        """Checks the isalistofdictionaries() method of
        util/html.py. Checks the equality of the result of an input.
        - in this case is checked the result, when the provided input is a
        list that its elements are not dictionaries.
        """

        self.assertFalse(util.html.
                         isalistofdictionaries(self.
                                                   not_list_of_dictionaries),
                         ('Testing isalistofdictionaries output. '
                          'Assert false 1'))

    def test03_isalistofdictionaries(self):
        """Checks the isalistofdictionaries() method of
        util/html.py. Checks the equality of the result of an input.
        - in this case is checked the result, when the provided input is not
        a list at all.
        """

        self.assertFalse(util.html.isalistofdictionaries(self.noise),
                         ('Testing isalistofdictionaries output. '
                          'Assert false 2'))

    @classmethod
    def tearDownClass(cls):
        """Cleans the testing environment parameters for Unittest
        class
        htmlIsAListOfDictionaries
        """
        pass

class HtmlMultyDictToHtml(unittest.TestCase):
    """Unittest class that tests the different functionalities of
    multy_dict_to_html() function in module util/html.py.
    """

    @classmethod
    def setUpClass(cls):
        """Initializes the testing environment parameters for the
        Unittest class htmlMultyDictToHtml.
        """

        cls.multy_dict_output = []
        cls.multy_dict_input = []
        cls.multy_dict_output.append('<table class="tableWithFloatingHeader">'
                                     '<thead><tr><th colspan="2" '
                                     'class="table-title">Test Table</th></tr>'
                                     '<tr><th>Throughput flowmods/sec</th>'
                                     '<th>switches</th></tr></thead><tbody>'
                                     '<tr><td>300</td><td>700</td></tr>'
                                     '<tr class="odd"><td>1000</td>'
                                     '<td>800</td></tr></tbody></table>')
        cls.data_fields = collections.OrderedDict()
        cls.data_fields['result2'] = 'Throughput flowmods/sec'
        cls.data_fields['result3'] = 'switches'
        cls.multy_dict_input.append(([{'result1':200, 'result2':300,
                                       'result3':700},
                                      {'result1':500, 'result2':1000,
                                       'result3':800}],
                                     'Test Table',
                                     cls.data_fields))
        cls.multy_dict_output.append('<table class="tableWithFloatingHeader">'
                                     '<thead><tr><th>result1</th><th>result2'
                                     '</th><th>result3</th></tr></thead>'
                                     '<tbody><tr><td>800</td><td>1000</td>'
                                     '<td>90</td></tr><tr class="odd">'
                                     '<td>9800</td><td>1900</td><td>900</td>'
                                     '</tr></tbody></table>')
        cls.row_data1 = collections.OrderedDict()
        cls.row_data1['result1'] = 800
        cls.row_data1['result2'] = 1000
        cls.row_data1['result3'] = 90
        cls.row_data2 = collections.OrderedDict()
        cls.row_data2['result1'] = 9800
        cls.row_data2['result2'] = 1900
        cls.row_data2['result3'] = 900
        cls.multy_dict_input.append([cls.row_data1, cls.row_data2])

    def test01_multy_dict_to_html(self):
        """Tests the multy_dict_to_html() method of util/html.py.
        It checks the equality of the result of an input.
        - In this test case we are using only the compulsory arguments of the
        method
        """
        self.\
        assertMultiLineEqual(self.multy_dict_output[0],
                             util.html.multi_dict_to_html(*self.
                                                          multy_dict_input[0]),
                             ('Testing multy_dict_to_'
                              'html_multiline output test 2'))

    def test02_multy_dict_to_html(self):
        """Tests the multy_dict_to_html() method of util/html.py.
        It checks the equality of the result of an input. In this test case we
        are using only the compulsory arguments of the method
        """
        self.\
        assertMultiLineEqual(self.multy_dict_output[1],
                             util.html.multi_dict_to_html(self.
                                                          multy_dict_input[1]),
                             ('Testing multy_dict'
                              '_to_html_multiline output test 2'))

    @classmethod
    def tearDownClass(cls):
        """Cleans the testing environment parameters
        """
        pass

class HtmlSingleDictToHtml(unittest.TestCase):
    """
    Unittest class to test the different functionalities of
    single_dict_to_html() function in module util/html.py.
    """

    def setUp(self):
        """
        Method that initializes the testing environment parameters for the
        Unittest class htmlSingleDictToHtml
        """
        self.data_row = collections.OrderedDict()
        self.data_row['row_title1'] = 'Throughput flowmods/sec'
        self.data_row['row_title3'] = 'switches'
        self.single_dict_output = ('<table  '
                                   'class="tableWithFloatingHeader">'
                                   '<thead><tr><th class="title" colspan=2">'
                                   'Test table</th></tr>'
                                   '<tr><th>Attributes</th>'
                                   '<th>Values</th></tr></thead><tbody><tr>'
                                   '<td style="font-weight:bold;">'
                                   'Throughput flowmods/sec</td><td>12</td>'
                                   '</tr></tbody></table>')
        self.single_dict_input = ({'row_title1':12, 'row_title2':45},
                                  'Attributes', 'Values',
                                  'Test table',
                                  self.data_row)

    def test01_single_dict_to_html(self):
        """
        Method that tests the single_dict_to_html() method of util/html.py
        It checks the equality of the result of an input.
        - In this test case we are testing all the features of the method
        """
        self.\
        assertMultiLineEqual(self.single_dict_output,
                             util.html.single_dict_to_html(*self.
                                                           single_dict_input),
                             ('Testing single_dict'
                              '_to_html_multiline output'))

    def tearDown(self):
        """
        Method that cleans the testing environment parameters for the Unittest
        class htmlSingleDictToHtml.
        """
        pass

class GetOrderedIndex(unittest.TestCase):
    """
    Unittest class to test the different functionalities of
    get_ordered_index() function in module util/html.py.
    """
    @classmethod
    def setUpClass(cls):
        """
        Method that initializes the testing environment parameters
        """
        cls.map_dict = collections.OrderedDict()
        cls.map_dict['result2'] = 'Throughput flowmods/sec'
        cls.map_dict['result3'] = 'switches'
        cls.map_dict['result4'] = 'switches'

    def test01_get_ordered_index(self):
        """Method that tests functionality of get_ordered_index() function
        in case where it returns a valid index"""
        self.assertEqual(1,
                         util.html.get_ordered_index('result3',
                                                     self.map_dict),
                         'Testing returned index when key exists.')

    def test02_get_ordered_index(self):
        """Method that tests functionality of get_ordered_index() function
        in case where it returns a invalid index (returns None)"""
        self.assertEqual(-1, util.html.get_ordered_index('result33',
                                                      self.map_dict),
                          'Testing returned index when key does not exist.')

    @classmethod
    def tearDownClass(cls):
        """
        Method that cleans the testing environment parameters
        """
        pass

class SingleDictTableData(unittest.TestCase):
    """
    Unittest class to test the different functionalities of
    single_dict_table_data() function in module util/html.py.
    """
    @classmethod
    def setUpClass(cls):
        """
        Method that initializes the testing environment parameters
        """
        cls.input1 = 'test data field'
        cls.output1 = ('<td style="font-size:bold;" class="info">test '
                       'data field</td>')
        cls.input2 = [{'title1':'value1_1', 'title2':'value1_1'},
                      {'title1':'value2_2', 'title2':'value2_2'}]
        cls.output2 = ('<td style="font-size:bold;" class="info">'
                       '<table class="tableWithFloatingHeader"><thead>'
                       '<tr><th></th><th></th></tr></thead><tbody><tr>'
                       '<td>value1_1</td></tr><tr class="odd">'
                       '<td>value1_1</td></tr></tbody>'
                       '</table><table class="tableWithFloatingHeader"><thead>'
                       '<tr><th></th><th></th></tr></thead><tbody><tr>'
                       '<td>value2_2</td></tr><tr class="odd">'
                       '<td>value2_2</td></tr></tbody></table></td>')
        cls.td_style = 'font-size:bold;'
        cls.td_class = 'info'

    def test_01_singledicttabledata(self):
        """
        Method that tests single_dict_table_data() when data_values parameter
        is a string value.
        """

        self.assertEqual(self.output1,
                         util.html.single_dict_table_data(self.input1,
                                                          self.td_style,
                                                          self.td_class),
                         'Testing single_dict_table_data() '
                         'with a string input.')

    def test_02_singledicttabledata(self):
        """
        Method that tests single_dict_table_data() when data_values parameter
        is a List of Dictionaries.
        """

        self.assertEqual(self.output2,
                         util.html.single_dict_table_data(self.input2,
                                                          self.td_style,
                                                          self.td_class),
                         'Testing single_dict_table_data() '
                         'with a List of Dictionaries.')

    @classmethod
    def tearDownClass(cls):
        """
        Method that cleans the testing environment parameters
        """
        pass

if __name__ == '__main__':

    SUITE_HTMLGENERATE_HTMLFOOT = \
    unittest.TestLoader().loadTestsFromTestCase(HtmlGenerateHtmlFoot)
    unittest.TextTestRunner(verbosity=2).run(SUITE_HTMLGENERATE_HTMLFOOT)

    SUITE_HTMLGENERATEDHEAD = \
    unittest.TestLoader().loadTestsFromTestCase(HtmlGenerateHead)
    unittest.TextTestRunner(verbosity=2).run(SUITE_HTMLGENERATEDHEAD)

    SUITE_HTMLISALISTOFFICTIONARIES = \
    unittest.TestLoader().loadTestsFromTestCase(HtmlIsAListOfDictionaries)
    unittest.TextTestRunner(verbosity=2).\
    run(SUITE_HTMLISALISTOFFICTIONARIES)

    SUITE_HTMLMUTLTIDICTTOHTML = \
    unittest.TestLoader().loadTestsFromTestCase(HtmlMultyDictToHtml)
    unittest.TextTestRunner(verbosity=2).run(SUITE_HTMLMUTLTIDICTTOHTML)

    SUITE_HTML_SINGLEDICTTOHTML = \
    unittest.TestLoader().loadTestsFromTestCase(HtmlSingleDictToHtml)
    unittest.TextTestRunner(verbosity=2).run(SUITE_HTML_SINGLEDICTTOHTML)

    SUITE_GETORDEREDINDEX = \
    unittest.TestLoader().loadTestsFromTestCase(GetOrderedIndex)
    unittest.TextTestRunner(verbosity=2).run(SUITE_GETORDEREDINDEX)

    SUITE_SINGLEDICTTABLEDATA = \
    unittest.TestLoader().loadTestsFromTestCase(SingleDictTableData)
    unittest.TextTestRunner(verbosity=2).run(SUITE_SINGLEDICTTABLEDATA)
