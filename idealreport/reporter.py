import htmltag
from idealreport import create_html


class Plotter(object):
    """ Class to wrap report plotting """

    def __init__(self, reporter=None):
        """ store the Reporter instance to allow adding HTML to the report stored internally in Reporter"""
        self.reporter = reporter

    def _add_labels(self, plot_dict, title, xlabel=None, ylabel=None):
        """ add standard labels to a plot dictionary - title is required """
        plot_dict['title'] = title
        if xlabel is not None:
            plot_dict['x'] = {'label': xlabel}
        if ylabel is not None:
            plot_dict['y'] = {'label': ylabel}
        return plot_dict

    def bar(self, df, title, xlabel=None, ylabel=None, stacked=False, horizontal=False):
        """  plot a df as a bar plot 
            Args:
                df (DataFrame)
                title, xlabel, ylabel (str): title is required and others are optional
        """

        # stacked vs normal bar plots
        plot_type = 'bar'
        if stacked:
            plot_type = 'stackedBar'

        # vertical vs horizontal bars
        orientation = 'v'
        if horizontal:
            orientation = 'h'

        # dict() to store info for plotting
        plot_dict = {
            'data': [{'df': df, 'type': plot_type, 'orientation': orientation}],
            'staticPlot': False
        }

        # plot labels + create HTML
        plot_dict = self._add_labels(plot_dict, title, xlabel, ylabel)
        if self.reporter:
            self.reporter.h += create_html.plot(plot_dict)
        return plot_dict

    def barh(self, df, title, xlabel=None, ylabel=None, stacked=False):
        """  plot a df as a horizontal bar plot 
            Args:
                df (DataFrame)
                title, xlabel, ylabel (str): title is required and others are optional
        """
        return self.bar(df, title, xlabel, ylabel, stacked, horizontal=True)

    def line(self, df, title, xlabel=None, ylabel=None, ):
        # dict() to store info for plotting
        plot_dict = {
            'data': [{'df': df, 'type': 'line'}],
            'staticPlot': False
        }

        # plot labels + create HTML
        plot_dict = self._add_labels(plot_dict, title, xlabel, ylabel)
        if self.reporter:
            self.reporter.h += create_html.plot(plot_dict)
        return plot_dict


    def scatter(self, df, title, xlabel=None, ylabel=None, ):
        # dict() to store info for plotting
        plot_dict = {
            'data': [{'df': df, 'type': 'scatter'}],
            'staticPlot': False
        }

        # plot labels + create HTML
        plot_dict = self._add_labels(plot_dict, title, xlabel, ylabel)
        if self.reporter:
            self.reporter.h += create_html.plot(plot_dict)
        return plot_dict

    def time(self, df, title, gap_time_format=None, xlabel=None, ylabel=None):
        """ plot a df as a timeseries 
            Args:
                df (DataFrame)
                gap_time_format (str): If specified, then skip gaps and format timestamps using this str
                title, xlabel, ylabel (str): title is required and others are optional
        """
        # remove nan and replace timestamps as strings to handle gaps in time
        if gap_time_format is not None:
            is_one_dim = (len(df.shape) == 1) or (df.shape[1] == 1)
            if is_one_dim:
                df = df[df.notnull()]
            else:
                df = df[df.notnull().any(axis=1)]
            df.index = df.index.map(lambda dt: dt.strftime(gap_time_format))

        # dict() to store info for plotting
        plot_dict = {
            'data': [{'df': df, 'type': 'line'}],
            'staticPlot': False
        }

        # plot labels + create HTML
        plot_dict = self._add_labels(plot_dict, title, xlabel, ylabel)
        if self.reporter:
            self.reporter.h += create_html.plot(plot_dict)
        return plot_dict


class Reporter(object):
    """ class to wrap the report class and add helper f()s - perhaps push functionality to the report class? """
    def __init__(self, title, output_file):
        self.title = title
        self.output_file = output_file
        # html string
        self.h = ''  
        # wrapper for plots, including a reference to this reporter instance to store HTML
        self.plot = Plotter(self)
        
    def pagebreak(self):
        """ add a page break to the html """
        self.h += create_html.pagebreak()
        
    #def plot(self):
    #    return self.plotWrap

    def row(self):
        """ add a row to the report (using the CSS grid) """
        return Row(self)
        
    def col(self, size):
        """ add a column to the report (using the CSS grid); 
            size should be between 1 and 11 (the grid system uses 12 columns) """
        return Column(self, size)
    
    def _add_plot_labels(self, plot_dict, title, xlabel=None, ylabel=None):
        """ add standard labels to a plot dictionary - title is required """
        plot_dict['title'] = title
        if xlabel is not None:
            plot_dict['x'] = {'label': xlabel}
        if ylabel is not None:
            plot_dict['y'] = {'label': ylabel}
        return plot_dict
                
    def text(self, text):
        """ append the specified text as html """
        self.h += htmltag.p(text)

    def filter_substr(start_list, filter_list):
        """ find all the items in start_list that contains any substr in filter_list
        Returns end_list, diff_list:
            end_list: all items in start_list that have matches
            diff_list: the difference between start_list and end_list (used for future f() calls)
        """
        end_list = []
        for f in filter_list:
            end_list.extend([x for x in start_list if f in x])
        return end_list, list(set(start_list) - set(end_list))
        
    def generate(self):
        """ generate and save the report HTML """
        create_html.save(self.h, self.title, self.output_file)
        print 'saved report to %s' % self.output_file    


class Row(object):
    """The Row class creates a row in the report using a CSS grid."""
    
    def __init__(self, reporter):
        self._reporter = reporter
        self._reporter.h += '<div class="row">\n'
        
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._reporter.h += '</div>\n'


class Column(object):
    """The Column class creates a col in the report using a CSS grid."""
        
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
