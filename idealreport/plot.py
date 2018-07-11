# The idealreport.plot module contains functions that all return python dictionaries 
# that specify plots. Users can create their own dictionaries and call create_html.plot()
# or use the functions below to create basic plot types

import idealreport

class PlotSpec:
    """ The PlotSpec class contains functions to create various standard plots:
            basic: line(), pie(), scatter(), time()
            bar charts: bar(), barh(), baro(), histogram()
            advanced: box(), errbar(), errline(), sankey()

        The output of the plot f()s will be:
            dict if return_html == False
            HTML text if return_html == True

        That dict can then used as an input to create_html.plot() 
    """
    def __init__(self, return_html=False):
        """ the store the Reporter instance to allow adding HTML to the report stored internally in Reporter"""
        self.return_html = return_html

    def _add_labels(self, plot_dict, title=None, x_label=None, y_label=None, y2_label=None):
        """ add standard labels to a plot dictionary - title is required """
        if title is not None:
            plot_dict['title'] = title
        if x_label is not None:
            plot_dict['x'] = {'label': x_label}
        if y_label is not None:
            plot_dict['y'] = {'label': y_label}
        if y2_label is not None:
            plot_dict['y2'] = {'label': y2_label}
        return plot_dict

    def _append_dict(self, plot_dict, dict_add_items):
        """ foc customized plots, append the items from dict_add_items to plot_dict
            e.g. layout, lines, opacities, etc.
            Args:
                plot_dict (dict): plot specs
                plot_dict (dict): customization items to add to the plot specs
            Returns:
                plot_dict (dict): plot specs, with additional items
        """
        for key, value in dict_add_items.iteritems():
            if value is not None:
                plot_dict[key] = value
        return plot_dict

    def _process_output(self, plot_dict):
        """ if specified in init(), return HTML. Default is to return a dict
            Returns:
                plot_dict unchanged, if self.return_html == False
                create_html.plot(plot_dict), if self.return_html == True
        """
        if self.return_html:
            return idealreport.create_html.plot(plot_dict)
        else:
            return self._process_output(plot_dict)

    def bar(self, df, title=None, x_label=None, y_label=None, stacked=False, horizontal=False, markers=None, widths=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as a bar chart
            Args:
                df (DataFrame): df with index as x axis
                title, x_label, y_label (str): title is required and others are optional
        """

        # stacked vs normal bar plots
        plot_type = 'stackedBar' if stacked else 'bar'

        # vertical vs horizontal bars
        orientation = 'h' if horizontal else 'v'

        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': plot_type, 'orientation': orientation}],}

        if data_static is not None:
            plot_dict['data'][0].update({'data_static':data_static})

        if data_to_iterate is not None:
            plot_dict['data'][0].update({'data_to_iterate':data_to_iterate})

        # append the custom layout, etc, if specified
        dict_add_items = {'layout': layout, 'markers': markers, 'widths': widths}
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items=dict_add_items)

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def barh(self, df, title=None, x_label=None, y_label=None, stacked=False, markers=None, widths=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as a horizontal bar chart
            Args:
                df (DataFrame): df with index as y axis
                title, x_label, y_label (str): title is required and others are optional
        """
        return self.bar(df=df, title=title, x_label=x_label, y_label=y_label, stacked=stacked, horizontal=True, markers=markers, widths=widths, data_static=data_static, data_to_iterate=data_to_iterate, layout=layout)

    def baro(self, df, title=None, x_label=None, y_label=None, orientation='v', markers=None, widths=None, opacities=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as an overlay bar chart
            Args:
                df (DataFrame): df with index as x axis for vertical, y axis for horizontal
                title, x_label, y_label (str): title is required and others are optional
        """

        plot_dict = {'data': [{'df': df, 'type': 'overlayBar', 'orientation': orientation}],}

        # static / iterate data for customized plots, e.g. univariate
        if data_static is not None:
            plot_dict['data'][0].update({'data_static':data_static})

        if data_to_iterate is not None:
            plot_dict['data'][0].update({'data_to_iterate':data_to_iterate})

        # append the custom layout, etc, if specified
        dict_add_items = {'layout': layout, 'markers': markers, 'opacities': opacities, 'widths': widths}
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items=dict_add_items)

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def box(self, df, title=None, groups = None, horizontal=False, markers=None, layout=None):

         # vertical vs horizontal box
        orientation = 'h' if horizontal else 'v'

        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'box', 'orientation': orientation, 'groups': groups}],}

        # append the custom layout and markers, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout, 'markers': markers})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title)
        return self._process_output(plot_dict)

    def errbar(self, df, title=None, x_label=None, y_label=None, symmetric=True, layout=None):
        """ plot a df as an error bar chart
            Args:
                df (DataFrame): df with index as x axis, column 1 as y value, column 2 as positive (or symmetric) error, column 3 as negative (optional) error
                title, x_label, y_label (str): title is required and others are optional
        """

        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'scatter', 'errorBars': {'symmetric': symmetric,}}],}

        # append the custom layout, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def errline(self, df, title=None, x_label=None, y_label=None, fillcolor='rgba(0,100,80,0.2)', layout=None):
        """ plot a df as a continuous error line chart
            Args:
                df (DataFrame): df with index as x axis, column 1 as y value, column 2 as symmetric error
                title, x_label, y_label (str): title is required and others are optional
                fillcolor (str rgba()): rgba value for fill, default is 'rgba(0,100,80,0.2)'
        """

        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'continuousErrorBars', 'fillcolor':fillcolor}],}

        # append the custom layout, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def histo(self, df, title=None, x_label=None, y_label=None, markers=None, layout=None):
        """ plot a df as a histogram
            Args:
                df (DataFrame): df with index as x axis
                title, x_label, y_label (str): title is required and others are optional
        """

        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'histogram'}],}

        # append the custom layout and markers, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout, 'markers': markers})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def line(self, df, title=None, x_label=None, y_label=None, lines=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as a line plot 
            Args:
                df (DataFrame): df with index as x axis
                title, x_label, y_label (str): title is required and others are optional
        """
        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'line'}],}

        if data_static is not None:
            plot_dict['data'][0].update({'data_static':data_static})

        if data_to_iterate is not None:
            plot_dict['data'][0].update({'data_to_iterate':data_to_iterate})

        # append the custom layout and lines, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout, 'lines': lines})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def multi(self, dfs, types, title=None, x_label=None, y_label=None, y2_axis=None, y2label=None, markers=None, widths=None, opacities=None, lines=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot multiple plot types on the same plot 
            Args:
                dfs (list of DataFrames)
                types (list of strings): list of plot types corresponding to dfs
                title, x_label, y_label (str): title is required and others are optional
                y2_axis (list of booleans): booleans indicating whether y values should be plotted on secondary y axis (optional)
                y2label (str): label for secondary y axis (optional)
        """
        data = []
        for i in range(len(dfs)):
            if y2_axis == None:
                data.append({'df':dfs[i], 'type':types[i]})
            else:
                data.append({'df':dfs[i], 'type':types[i], 'y2':y2_axis[i]})

            # data_static and data_to_iterate need to be appending df by df to the data dict
            if data_static is not None:
                if len(data_static) > i:
                    if data_static[i] is not None:
                        data[i].update({'data_static':data_static[i]})
            if data_to_iterate is not None:
                if len(data_to_iterate) > i:
                    if data_to_iterate[i] is not None:
                        data[i].update({'data_to_iterate':data_to_iterate[i]})

        # dict() to store info for plotting
        plot_dict = {'data': data,}

        # append the custom layout, etc, if specified
        dict_add_items = {'layout': layout, 'lines': lines, 'markers': markers, 'opacities': opacities, 'widths': widths}
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items=dict_add_items)

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label, y2label)
        return self._process_output(plot_dict)

    def ohlc(self, df, title=None, series_name = '', x_label=None, y_label=None, layout=None):
        """ timeseries OHLC
            Args:
                df (DataFrame): df requires columns open, high, low, close
                title, x_label, y_label (str): title is required and others are optional
        """
        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'ohlc'}], 'name': series_name}

        # append the custom layout, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def pie(self, df, title=None, hole=None, markers=None, margin=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as a pie chart 
            Args:
                df (DataFrame): df with index as label / category, first column as value
                title (str): title is required and others are optional
                hole (num [0-1]): percentage of pie to cut out for donut (optional)
        """
        if hole is not None:
            plot_dict = {'data': [{'df': df, 'type': 'pie', 'hole': hole}],}
        else:
            plot_dict = {'data': [{'df': df, 'type': 'pie'}],}

        if data_static is not None:
            plot_dict['data'][0].update({'data_static':data_static})

        if data_to_iterate is not None:
            plot_dict['data'][0].update({'data_to_iterate':data_to_iterate})

        # append the custom layout and markers, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout, 'markers': markers})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title)        
        return self._process_output(plot_dict)

    def sankey(self, df, title=None, node=None, link_labels=[], vertical=False, layout=None):

        # vertical vs horizontal box
        orientation = 'v' if vertical else 'h'

        # dict() to store info for plotting
        plot_dict = {
            'data': [{'df': df, 'type': 'sankey', 'orientation': orientation, 'linkLabels': link_labels}],
            'type': 'sankey',
            'node': node
        }

        # append the custom layout, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title)
        return self._process_output(plot_dict)

    def scatter(self, df, title=None, x_label=None, y_label=None, markers=None, margin=None, hide_legend=False, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as a scatter plot 
            Args:
                df (DataFrames): df with index as x axis
                title, x_label, y_label (str): title is required and others are optional
        """
        # dict() to store info for plotting
        plot_dict = {'data': [{'df': df, 'type': 'scatter'}],}

        if data_static is not None:
            plot_dict['data'][0].update({'data_static':data_static})

        if data_to_iterate is not None:
            plot_dict['data'][0].update({'data_to_iterate':data_to_iterate})

        # append the custom layout, etc, if specified
        dict_add_items = {'hide_legend': hide_legend, 'layout': layout, 'margin': margin, 'markers': markers}
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items=dict_add_items)

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)

    def time(self, df, title=None, gap_time_format=None, x_label=None, y_label=None, lines=None, data_static=None, data_to_iterate=None, layout=None):
        """ plot a df as a timeseries 
            Args:
                df (DataFrame): df with index as x axis
                gap_time_format (str): If specified, then skip gaps and format timestamps using this str
                title, x_label, y_label (str): title is required and others are optional
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
        plot_dict = {'data': [{'df': df, 'type': 'line'}],}

        if data_static is not None:
            plot_dict['data'][0].update({'data_static':data_static})

        if data_to_iterate is not None:
            plot_dict['data'][0].update({'data_to_iterate':data_to_iterate})

        # append the custom layout and markers, if specified
        plot_dict = self._append_dict(plot_dict=plot_dict, dict_add_items={'layout': layout, 'lines': lines})

        # plot labels
        plot_dict = self._add_labels(plot_dict, title, x_label, y_label)
        return self._process_output(plot_dict)