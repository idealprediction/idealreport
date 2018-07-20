""" idealreport.create_html module contains functions to
    convert pandas DataFrame data to HTML
"""

import os
import json
import shutil

# external libraries
import htmltag
import jinja2


# a counter used to assign each plot a unique ID
NEXT_PLOT_INDEX = 1


def save(html, title, output_file):
    """ save HTML output; copies files into the directory containing the output file """
    global NEXT_PLOT_INDEX

    # the HTML library (css/js) path is relative to this module
    lib_path = os.path.dirname(__file__)

    # create output directory if needed
    output_path = os.path.dirname(output_file)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # copy files referenced by HTML file into output directory
    source_path = lib_path + '/htmlLibs'
    file_list = os.listdir(source_path)
    for fn in file_list:
        shutil.copy(source_path + '/' + fn, output_path + '/' + fn)

    # fill the template
    template_contents = open(lib_path + '/template.html').read()
    template = jinja2.Template(template_contents)
    html = template.render(title=title, contents=str(html))

    # save the html file to disk
    open(output_file, 'w').write(html)

    # reset the plot counter
    NEXT_PLOT_INDEX = 1


# ======== HTML generating functions (all return HTML string) ========


def frequency_table(item_counts, name, max_items=10):
    """ create a table of item frequencies """

    # create header
    row = htmltag.tr(htmltag.th(name), htmltag.th('Count'))
    thead = htmltag.thead(row)

    # add items
    trs = []
    items = [(v, k) for (k, v) in item_counts.items()]
    items.sort(reverse=True)
    if len(items) > max_items:
        items = items[:max_items]
    for (value, key) in items:
        row = htmltag.tr(htmltag.td(key), htmltag.td(str(value)))
        trs.append(row)
    tbody = htmltag.tbody(*trs)
    return htmltag.table(thead, tbody)


def pagebreak():
    """ create a page break (will show up when printing to pdf) """
    return htmltag.div('', style="page-break-after:always;")


def paragraph(text):
    """ wrap the text in a paragraph """
    return htmltag.p(text)


def plot(plot_spec):
    """ create a plot by storing the data in a json file and returning HTML for displaying the plot """
    global NEXT_PLOT_INDEX

    # compute an ID for this plot
    plot_id = 'plot%d' % NEXT_PLOT_INDEX
    NEXT_PLOT_INDEX += 1

    # process the dictionary of plot specifications
    plot_spec = prep_plot_spec(plot_spec)

    # create HTML
    h = htmltag.div('', id=plot_id)
    h += htmltag.script('var g_%s = %s;\ngeneratePlot("%s", g_%s);' % (plot_id, json.dumps(plot_spec), plot_id, plot_id))
    return h


def table(df, sortable=False, last_row_is_footer=False, col_format=None):
    """ generate an HTML table from a pandas data frame
        Args:
            df (df): pandas DataFrame
            col_format (dict): format the column name (key)
                                using the format string (value)
        Returns:
            HTML (str)
    """
    if col_format is None:
        col_format = {}
    row_count = len(df)

    # default column formatting
    default_format = {
        'align': 'right',
        'decimal_places': 2,
        'commas': True,
        'width': None,
    }

    def get_format(col, attribute):
        """ helper function to get column formatting
            Args:
                col: column name (key in the col_format)
                attribute (str)
            Returns:
                format (str) for the specified col
        """
        if col in col_format and attribute in col_format[col_name]:
            value = col_format[col_name][attribute]
        elif '*' in col_format and attribute in col_format['*']:
            value = col_format['*'][attribute]
        else:
            value = default_format[attribute]
        return value

    # create header
    items = []
    # if there's a hierarchical index for the columns, span the top level; only suppots 2 levels
    if isinstance(df.columns[0], tuple):
        headers = []
        prev_header = df.columns[0][0]
        span = 0
        for i, col_name in enumerate(df.columns):
            h1 = col_name[0]
            h2 = col_name[1]
            if h1 == prev_header:
                span += 1
                if i == (len(df.columns)-1):
                    headers.append(htmltag.th(h1, colspan=span, _class='centered'))
            else:
                headers.append(htmltag.th(prev_header, colspan=span, _class='centered'))
                if i == (len(df.columns)-1):
                    headers.append(htmltag.th(h1, colspan=1))
                else:
                    prev_header = h1
                    span = 1

            if get_format(col_name, 'align') == 'right':
                items.append(htmltag.th(h2, _class='alignRight'))
            else:
                items.append(htmltag.th(h2))
        thead = htmltag.thead(htmltag.tr(*headers), htmltag.tr(*items))

    else:
        for col_name in df.columns:
            if get_format(col_name, 'align') == 'right':
                if sortable:
                    items.append(htmltag.th(col_name, **{'class':'alignRight', 'data-sortable':'true'}))
                else:
                    items.append(htmltag.th(col_name, _class='alignRight'))
            else:
                if sortable:
                    items.append(htmltag.th(col_name, **{'data-sortable':'true'}))
                else:
                    items.append(htmltag.th(col_name))

        thead = htmltag.thead(htmltag.tr(*items))

    # create body (and optionally footer)
    tfoot = ''
    rows = []
    for i, row in df.iterrows():
        values = row.tolist()
        items = []
        for j, v in enumerate(values):
            col_name = df.columns[j]
            if is_numeric(v):
                decimal_places = get_format(col_name, 'decimal_places')
                if get_format(col_name, 'commas'):
                    pattern = '{:,.' + str(decimal_places) + 'f}'
                else:
                    pattern = '{:.' + str(decimal_places) + 'f}'
                v = pattern.format(v)
            if get_format(col_name, 'align') == 'right':
                items.append(htmltag.td(v, _class='alignRight'))
            # TODO - need to implement width control
            #width = get_format(col_name, 'width')
            #if is_numeric(width):
            #    style='width:' + str(width) + 'px'
            #    items.append(htmltag.td(v, style=style ))
            else:
                items.append(htmltag.td(v))
        if last_row_is_footer and i == row_count - 1:
            tfoot = htmltag.tfoot(htmltag.tr(*items))
        else:
            rows.append(htmltag.tr(*items))
    tbody = htmltag.tbody(*rows)
    # if sortable, apply the bootstrap-table tab, bs-table
    if sortable:
        if row_count > 15:
            return htmltag.table(thead, tbody, tfoot, **{'class':'bs-table', 'data-striped':'true', 'data-height':'600'})
        else:
            return htmltag.table(thead, tbody, tfoot, **{'class':'bs-table', 'data-striped':'true'})
    else:
        return htmltag.table(thead, tbody, tfoot, **{'class':'table-striped'})


# ======== report spec functions ========


def prep_plot_spec(plot_spec):
    """ process the dictionary of plot specifications """

    # make a copy of the plot spec (except data) so that we can re-generate
    # a report without regenerating the plot specs
    # (converting the data frames will take place only in this copy)
    data_specs = plot_spec.get('data', [])
    plot_spec = {k: v for (k, v) in plot_spec.items() if k != 'data'} # copy all but data
    plot_spec['data'] = []

    # get original value for timestamp type
    time_x = (plot_spec.get('typeX', 'none') == 'timestamp')

    # convert data frames
    for ds in data_specs:
        # check for timestamp index
        df = ds['df']
        time_df = df.index.dtype == 'datetime64[ns]'
        if time_x and not time_df:
            raise Exception('typeX is timestamp but df has non-timestamp index')
        if time_df:
            time_x = True

        # create new data spec with df converted to dict/lists for json
        new_data_spec = {k: v for (k, v) in ds.items() if k != 'df'} # copy all but df
        new_data_spec['df'] = dataframe_to_dict(df)
        plot_spec['data'].append(new_data_spec)

    # set timestamp type
    if time_x:
        plot_spec['typeX'] = 'timestamp'

    # check for out-of-date API calls
    for ds in data_specs:
        if 'format' in ds:
            print 'warning: format in data spec no longer supported'

    return plot_spec


# ======== utility functions ========


def dataframe_to_dict(df):
    """ convert a pandas DataFrame (or series) to a list of columns ready for conversion to JSON """
    # assume df is a pd.DataFrame if it contains "columns", else it is a pd.Series
    columns = []
    if hasattr(df, 'columns'): # data frame
        columns.append({ # index
            'name': df.index.name,
            'values': json.loads(df.to_json(orient='split', date_format='iso'))['index']
        })
        for col in df.columns: # columns
            columns.append({
                'name': col,
                'values': json.loads(df[col].to_json(orient='values', date_format='iso'))
            })
    else: # series
        series = df
        columns.append({ # index
            'name': series.index.name,
            'values': json.loads(series.to_json(orient='split', date_format='iso'))['index']
        })
        columns.append({ # values
            'name': series.name,
            'values': json.loads(series.to_json(orient='values', date_format='iso'))
        })
    return columns


def is_numeric(value):
    """ check whether a value is numeric (could be float, int, or numpy numeric type) """
    return hasattr(value, '__sub__') and hasattr(value, '__mul__')
