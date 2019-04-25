""" The reporter module contains:
    Reporter class to create HTML reports
    Row to add an HTML row
    Col to add an HTML column
"""

import idealreport


class Reporter(object):
    """ class to create HTML reports
        Attributes:
            title (str): report title
            output_file (str): full name of the resulting HTML file
            h (str): string of HTML
            plot (idealreport.plot.PlotSpec): creates HTML of plots
    """
    def __init__(self, title, output_file):
        self.title = title
        self.output_file = output_file
        # html string
        self.h = ''
        # wrapper for plots, specifying to return HTML (instead of plot_spec dict)
        self.plot = idealreport.plot.PlotSpec(return_html=True)

    def col(self, size):
        """ add a column to the report (using the CSS grid)
            size should be between 1 and 11 (the grid system uses 12 columns) """
        return Column(self, size)

    def generate(self):
        """ generate and save the report HTML """
        idealreport.create_html.save(self.h, self.title, self.output_file)
        print('saved report to %s' % self.output_file)

    def pagebreak(self):
        """ add a page break to the html """
        self.h += idealreport.create_html.pagebreak()

    def row(self):
        """ add a row to the report (using the CSS grid) """
        return Row(self)

    def text(self, text):
        """ append the specified text as html """
        self.h += idealreport.create_html.paragraph(text)


class Row(object):
    """ The Row class creates a row in the report using a CSS grid """
    def __init__(self, reporter):
        self._reporter = reporter
        self._reporter.h += '<div class="row">\n'

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._reporter.h += '</div>\n'


class Column(object):
    """ The Column class creates a col in the report using a CSS grid """
    def __init__(self, reporter, size):
        self._reporter = reporter
        assert size >= 1 and size <= 11
        col_sizes = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']
        size = col_sizes[size - 1]
        self._reporter.h += '<div class="%s columns">\n' % size

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._reporter.h += '</div>\n'
