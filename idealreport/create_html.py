import os
import json
import shutil
import datetime

# external libraries
import htmltag
import jinja2
import numpy as np


# a counter used to assign each plot a unique ID
next_plot_index = 1


def frequency_table(item_counts, name, sort=True, max_items=10):
    """ create a table of item frequencies """

    # create header
    tr = htmltag.tr(htmltag.th(name), htmltag.th('Count'))
    thead = htmltag.thead(tr)

    # add items
    trs = []
    items = [(v, k) for (k, v) in item_counts.items()]
    items.sort(reverse = True)
    if len(items) > max_items:
        items = items[:max_items]
    for (value, key) in items:
        tr = htmltag.tr(htmltag.td(key), htmltag.td(str(value)))
        trs.append(tr)
    tbody = htmltag.tbody(*trs)
    return htmltag.table(thead, tbody)


def pagebreak():
    """ create a page break (will show up when printing to pdf) """
    return htmltag.div('', style = "page-break-after:always;")


def plot(plot_spec):
    """ create a plot by storing the data in a json file and returning HTML for displaying the plot """
    global next_plot_index
    
    # compute an ID for this plot
    id = 'plot%d' % next_plot_index
    next_plot_index += 1
    
    plot_spec = prep_plot_spec(plot_spec)
    
    # create HTML
    h = htmltag.div('', id = id)
    h += htmltag.script('var g_%s = %s;\ngeneratePlot("%s", g_%s);' % (id, json.dumps(plot_spec), id, id))
    return h


def save(html, title, output_file):
    """ save HTML output; copies files into the directory containing the output file """
    global next_plot_index
    
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
    html = template.render(title = title, contents = str(html))
    
    # save the html file to disk
    open(output_file, 'w').write(html)
    
    # reset the plot counter
    next_plot_index = 1


def table(df, last_row_is_footer=False, format=None):
    """ generate an HTML table from a pandas data frame """
    if not format:
        format = {}
    rowCount = len(df)
    
    # default column formatting
    default_format = {
        'align': 'right',
        'decimal_places': 2,
        'commas': True,
    }
    
    # a helper function to get column formatting
    def get_format(col_name, attribute):
        if col_name in format and attribute in format[col_name]:
            value = format[col_name][attribute]
        elif '*' in format and attribute in format['*']:
            value = format['*'][attribute]
        else:
            value = default_format[attribute]
        return value
    
    # create header
    first = True
    items = []
    for col_name in df.columns:
        if get_format(col_name, 'align') == 'right':
            items.append(htmltag.th(col_name, _class='alignRight'))
        else:
            items.append(htmltag.th(col_name))
        first = False
    thead = htmltag.thead(htmltag.tr(*items))
        
    # create body (and optionally footer)
    tfoot = ''
    rows = []
    for i, row in df.iterrows():
        values = row.tolist()
        if False: # 
            tf = t.tfoot
            tr = tf.tr
        first = True
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
            else:
                items.append(htmltag.td(v))
            first = False
        if last_row_is_footer and i == rowCount - 1:
            tfoot = htmltag.tfoot(htmltag.tr(*items))
        else:
            rows.append(htmltag.tr(*items))
    tbody = htmltag.tbody(*rows)
    return htmltag.table(thead, tbody, tfoot)

    
# ======== report spec functions ========


def prep_plot_spec(plot_spec):

    # make a copy of the plot spec (except data) so that we can re-generate a report without regenerating the plot specs
    # (converting the data frames will take place only in this copy)
    data_specs = plot_spec.get('data', [])
    plot_spec = {k:v for (k,v) in plot_spec.items() if k != 'data'} # copy all but data
    plot_spec['data'] = []
    
    # get original value for timestamp type
    time_x = (plot_spec.get('typeX', 'none') == 'timestamp')
    
    # convert data frames
    for ds in data_specs:
    
        # check for timestamp index
        df = ds['df']
        time_df = df.index.dtype == 'datetime64[ns]'
        if time_x and not time_df:
            raise Exception( 'typeX is timestamp but df has non-timestamp index' )
        if time_df:
            time_x = True
        
        # create new data spec with df converted to dict/lists for json
        new_data_spec = {k:v for (k,v) in ds.items() if k != 'df'} # copy all but df
        new_data_spec['df'] = dataframe_to_dict(df)
        plot_spec['data'].append(new_data_spec)
        
        # check timestamps
     
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
    columns = []
    if hasattr(df, 'columns'): # data frame
        columns.append({ # index
            'name': df.index.name,
            'values': json.loads(df.to_json(orient='split', date_format='iso'))['index']
        })       
        for columnName in df.columns: # columns
            columns.append({
                'name': columnName,
                'values': json.loads(df[columnName].to_json(orient='values', date_format='iso'))
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


def is_numeric(v):
    """ check whether a value is numeric (could be float, int, or numpy numeric type) """
    return hasattr(v, '__sub__') and hasattr(v, '__mul__')
