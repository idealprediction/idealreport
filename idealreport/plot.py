""" The idealreport.plot module contains the PlotSpec class to generate either:
    1) python dictionaries that are later used by create_html.plot() to generate HTML
    2) HTML
"""

import idealreport


class PlotSpec(object):
    """ The PlotSpec class contains functions to create various standard plots:
            basic: line(), pie(), scatter(), time()
            bar charts: bar(), barh(), baro(), histogram()
            advanced: box(), errbar(), errline(), sankey()

        The output of the class functions will be:
            dict if return_html == False
            HTML if return_html == True

        note: the dict output can be used as an input to create_html.plot()

        This class is designed to enable users to create plots using concise code. 
        For more extensive control (and verbose code), users can directly create their
        own dictionaries and call create_html.plot(). 

        See sample_plots.py for examples.
    """
    def __init__(self, return_html=False):
        """ store a boolean that determines if the PlotSpec f()s will return a dict or HTML"""
        self.return_html = return_html

    def _add_labels(self, plot_dict, title=None, x_label=None, y_label=None, y2_label=None):
        """ add standard labels to a plot dictionary
            Args:
                plot_dict (dict): dictionary of plot specifications
                title (str): plot title
                x_label (str): label for the x axis
                y_label (str): label for the y axis
                y2_label (str): label for the second (right) y axis
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        if title is not None:
            plot_dict['title'] = title
        if x_label is not None:
            plot_dict['x'] = {'label': x_label}
        if y_label is not None:
            plot_dict['y'] = {'label': y_label}
        if y2_label is not None:
            plot_dict['y2'] = {'label': y2_label}
        return plot_dict

    def _customize_data(self, plot_dict, custom_data):
        """ customize the plot data
            This f() appends items from custom_data to plot_dict['data'] e.g. plot_dict['data'][0]['data_to_iterate']
            Args:
                plot_dict (dict): dictionary of plot specifications
                custom_data (dict): customization items to add to the plot specs data
                                        valid keys are ['data_to_iterate', 'data_static']
            Returns:
                plot_dict (dict): dictionary of plot specifications (with customized items)
            Raises:
                Exception if the custom_data contains keys that are not in ['data_to_iterate', 'data_static']
                Exception if plot_dict['data'] does not exist or is not of length 1
        """
        if custom_data is not None:
            # verify the custom_design contains keys that are expected for this plot type
            expect = ['data_to_iterate', 'data_static']
            if not set(custom_data.keys()).issubset(set(expect)):
                raise Exception('idealreport.plot._customize_data() custom dictionary contains keys %s that are not in the expected set %s' % (custom_data.keys(), expect))

            # check that the data field has already been set in the plot specifications and length is 1
            if 'data' not in plot_dict:
                raise Exception('idealreport.plot._customize_data() plot_dict is expected to already be populated with a "data" key')
            if len(plot_dict['data']) != 1:
                raise Exception('idealreport.plot._customize_data() len(plot_dict["data"]) must be 1')

            # append the custom dictionary to plot_dict['data'][0]
            plot_dict['data'][0].update(custom_data)

        return plot_dict

    def _customize_design(self, plot_dict, custom_design, expect):
        """ customize the plot design
            This f() appends items from custom_design to plot_dict e.g. plot_dict['layout'], plot_dict['lines']
            Args:
                plot_dict (dict): dictionary of plot specifications
                custom_design (dict): customization items to add to the plot specs
                expect (list): list of expected keys in the custom_design for this plot type, e.g. ['layout', 'markers']
            Returns:
                plot_dict (dict): dictionary of plot specifications (with customized items)
            Raises:
                Exception if the custom_design contains keys that are not in the "expect" list
        """
        if custom_design is not None:
            # verify the custom_design contains keys that are expected for this plot type
            if not set(custom_design.keys()).issubset(set(expect)):
                raise Exception('idealreport.plot._customize_design() custom dictionary contains keys %s that are not in the expected set %s' % (custom_design.keys(), expect))

            # append the custom dictionary to plot_dict
            plot_dict.update(custom_design)

        return plot_dict

    def _process_output(self, plot_dict):
        """ if specified in init(), return HTML. Default is to return a dict
            Args:
                plot_dict (dict): dictionary of plot specifications
            Returns:
                plot_dict unchanged, if self.return_html == False
                create_html.plot(plot_dict), if self.return_html == True
        """
        if self.return_html:
            return idealreport.create_html.plot(plot_dict)
        else:
            return plot_dict

    def bar(self, df, title=None, x_label=None, y_label=None, stacked=False, horizontal=False, custom_design=None, custom_data=None):
        """ bar chart
            Args:
                df (DataFrame): df 
                title, x_label, y_label (str): plot labels (optional)
                stacked (bool): True --> stacked bar chart (default False)
                horizontal (bool): True / False --> horizontal / vertical bar
                custom_design (dict): dictionary to customize the design
                                      expecting keys in set(['layout', 'markers', 'widths'])
                custom_data (dict): dictionary of custom data
                                    expecting keys in set(['data_to_iterate', 'data_static'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """

        # stacked vs normal bar plots
        plot_type = 'stackedBar' if stacked else 'bar'

        # vertical vs horizontal bars
        orientation = 'h' if horizontal else 'v'

        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': plot_type, 'orientation': orientation}],}
        plot_dict = self._customize_data(plot_dict=plot_dict, custom_data=custom_data)

        # labels and customize the plot, if specified
        expect = ['layout', 'markers', 'widths']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def baroverlay(self, df, title=None, x_label=None, y_label=None, orientation='v', custom_data=None, custom_design=None):
        """ overlay bar chart
            Args:
                df (DataFrame): df (index will be the x-axis)
                title, x_label, y_label (str): plot labels (optional)
                stacked (bool): True --> stacked bar chart (default False)
                horizontal (bool): True / False --> horizontal / vertical bar
                custom_design (dict): customize, expecting keys in set(['layout', 'markers', 'widths'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """

        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'overlayBar', 'orientation': orientation}],}
        plot_dict = self._customize_data(plot_dict=plot_dict, custom_data=custom_data)

        # labels and customize the plot, if specified
        expect = ['layout', 'markers', 'opacities', 'widths']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def box(self, df, title=None, groups=None, horizontal=False, custom_design=None):
        """ box plot
            Args:
                df (DataFrame): df
                title (str): plot labels (optional)
                groups: TODO
                horizontal (bool): True / False --> horizontal / vertical 
                custom_design (dict): customize, expecting keys in set(['layout', 'markers'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # vertical vs horizontal box
        orientation = 'h' if horizontal else 'v'

        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'box', 'orientation': orientation, 'groups': groups}],}

        # labels and customize the plot, if specified
        expect = ['layout', 'markers']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title)
        return self._process_output(plot_dict)

    def errbar(self, df, title=None, x_label=None, y_label=None, symmetric=True, custom_design=None):
        """ error bar chart
            Args:
                df (DataFrame): df (index will be the x-axis)
                title, x_label, y_label (str): plot labels (optional)
                stacked (bool): True --> stacked bar chart (default False)
                symmetric (bool): True / False --> symmetric/unsymmetric error bars around mean (default True)
                custom_design (dict): customize, expecting keys in set(['layout'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'scatter', 'errorBars': {'symmetric': symmetric,}}],}

        # labels and customize the plot, if specified
        expect = ['layout']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def errline(self, df, title=None, x_label=None, y_label=None, fillcolor='rgba(0,100,80,0.2)', custom_design=None):
        """ continuous error line
            Args:
                df (DataFrame): df (index will be the x-axis)
                title, x_label, y_label (str): plot labels (optional)
                fillcolor (str): rgba value for fill, default is 'rgba(0,100,80,0.2)'
                custom_design (dict): customize, expecting keys in set(['layout'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """

        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'continuousErrorBars', 'fillcolor':fillcolor}],}

        # labels and customize the plot, if specified
        expect = ['layout']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def histogram(self, df, title=None, x_label=None, y_label=None, custom_design=None):
        """ error bar chart
            Args:
                df (DataFrame): df 
                title, x_label, y_label (str): plot labels (optional)
                custom_design (dict): customize, expecting keys in set(['layout'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """

        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'histogram'}],}

        # labels and customize the plot, if specified
        expect = ['layout', 'markers']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def line(self, df, title=None, x_label=None, y_label=None, custom_data=None, custom_design=None):
        """ line plot
            Args:
                df (DataFrame): df (index will be the x-axis)
                title, x_label, y_label (str): plot labels (optional)
                custom_design (dict): customize, expecting keys in set(['layout', 'markers', 'widths'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'line'}],}
        plot_dict = self._customize_data(plot_dict=plot_dict, custom_data=custom_data)

        # labels and customize the plot, if specified
        expect = ['layout', 'lines']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def multi(self, dfs, types, title=None, x_label=None, y_label=None, y2_label=None, y2_axis=None, custom_data=None, custom_design=None):
        """ multiple types (line, bar, etc) on a single plot
            Args:
                df (DataFrame): list of DataFrames
                types (list of strings): list of plot types corresponding to dfs
                title, x_label, y_label, y2_label (str): plot labels (optional)
                y2_axis (list of booleans): booleans indicating whether y values should be plotted on secondary y axis (optional)
                custom_design (dict): customize, expecting keys in set(['layout', 'lines', 'markers', 'opacities', 'widths'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # list of data for plot specifications
        data_static = None
        data_to_iterate = None
        if custom_data is not None:
            data_static = custom_data['data_static']
            data_to_iterate = custom_data['data_to_iterate']
        data = []
        for i in range(len(dfs)):
            if y2_axis is None:
                data.append({'df': dfs[i], 'type': types[i]})
            else:
                data.append({'df': dfs[i], 'type': types[i], 'y2': y2_axis[i]})

            # data_static and data_to_iterate need to be appending df by df to the data dict
            if data_static is not None:
                if len(data_static) > i:
                    if data_static[i] is not None:
                        data[i].update({'data_static': data_static[i]})
            if data_to_iterate is not None:
                if len(data_to_iterate) > i:
                    if data_to_iterate[i] is not None:
                        data[i].update({'data_to_iterate': data_to_iterate[i]})

        # plot specifications
        plot_dict = {'data': data}

        # labels and customize the plot, if specified
        expect = ['layout', 'lines', 'markers', 'opacities', 'widths']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict=plot_dict, title=title, x_label=x_label, y_label=y_label, y2_label=y2_label)
        return self._process_output(plot_dict)

    def ohlc(self, df, title=None, x_label=None, y_label=None, custom_design=None):
        """ open high low close (OHLC) plot
            Args:
                df (DataFrame): df with required columns ['open', 'high', 'low', 'close']
                title, x_label, y_label, (str): plot labels (optional)
                custom_design (dict): customize, expecting keys in set(['layout', 'lines'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # plot specifications
        # TODO: use 'name'? plot_dict = {'data': [{'df': df, 'type': 'ohlc'}], 'name': series_name}
        plot_dict = {'data': [{'df': df, 'type': 'ohlc'}]}

        # labels and customize the plot, if specified
        expect = ['layout', 'lines']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def pie(self, df, title=None, hole=None, custom_data=None, custom_design=None):
        """ pie chart
            Args:
                df (DataFrame): df
                hole (num [0-1]): percentage of pie to cut out for donut (optional)
                title (str): plot labels (optional)
                custom_design (dict): customize, expecting keys in set(['layout', 'lines'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # plot specifications
        if hole is not None:
            plot_dict = {'data': [{'df': df, 'type': 'pie', 'hole': hole}],}
        else:
            plot_dict = {'data': [{'df': df, 'type': 'pie'}],}
        plot_dict = self._customize_data(plot_dict=plot_dict, custom_data=custom_data)

        # labels and customize the plot, if specified
        expect = ['layout', 'margin', 'markers']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title)
        return self._process_output(plot_dict)

    def sankey(self, df, title=None, node=None, link_labels=[], horizontal=True, custom_design=None):
        """ sankey chart
            Args:
                df (DataFrame): df
                title (str): plot labels (optional)
                link_labels (list): list of labels for the various links
                custom_design (dict): customize, expecting keys in set(['layout'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # vertical vs horizontal bars
        orientation = 'h' if horizontal else 'v'

        # plot specifications
        plot_dict = {
            'data': [{'df': df, 'type': 'sankey', 'orientation': orientation, 'linkLabels': link_labels}],
            'type': 'sankey',
            'node': node
        }

        # labels and customize the plot, if specified
        expect = ['layout']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict=plot_dict, title=title)
        return self._process_output(plot_dict)

    def scatter(self, df, title=None, x_label=None, y_label=None, custom_data=None, custom_design=None):
        """ scatter
            Args:
                df (DataFrame): df (index will be the x-axis)
                title, x_label, y_label (str): plot labels (optional)
                custom_design (dict): customize, expecting keys in set(['layout', 'markers', 'widths'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'scatter'}]}
        plot_dict = self._customize_data(plot_dict=plot_dict, custom_data=custom_data)

        # labels and customize the plot, if specified
        expect = ['layout', 'margin', 'markers']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def time(self, df, time_format=None, title=None, x_label=None, y_label=None, lines=None, custom_data=None, custom_design=None):
        """ time series
            Args:
                df (DataFrame): df (index will be the x-axis)
                time_format (str): If specified, skip gaps (e.g. weekends) and format timestamps using this str
                title, x_label, y_label (str): plot labels (optional)
                custom_design (dict): customize, expecting keys in set(['layout', 'markers', 'widths'])
            Returns:
                plot_dict (dict): dictionary of plot specifications
        """
        # remove nan and replace timestamps as strings to handle gaps in time
        if time_format is not None:
            is_one_dim = (len(df.shape) == 1) or (df.shape[1] == 1)
            if is_one_dim:
                df = df[df.notnull()]
            else:
                df = df[df.notnull().any(axis=1)]
            df.index = df.index.map(lambda dt: dt.strftime(gap_time_format))

        # plot specifications
        plot_dict = {'data': [{'df': df, 'type': 'line'}],}
        plot_dict = self._customize_data(plot_dict=plot_dict, custom_data=custom_data)

        # labels and customize the plot, if specified
        expect = ['layout', 'lines']
        plot_dict = self._customize_design(plot_dict=plot_dict, custom_design=custom_design, expect=expect)
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)
