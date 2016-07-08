import os
import json
import shutil
import datetime

# external libraries
import htmltag
import jinja2
import numpy as np


# a counter used to assign each plot a unique ID
nextPlotIndex = 1


def frequencyTable(itemCounts, name, sort=True, maxItems=10):
    """ create a table of item frequencies """

    # create header
    tr = htmltag.tr(htmltag.th(name), htmltag.th('Count'))
    thead = htmltag.thead(tr)

    # add items
    trs = []
    items = [(v, k) for (k, v) in itemCounts.items()]
    items.sort(reverse = True)
    if len(items) > maxItems:
        items = items[:maxItems]
    for (value, key) in items:
        tr = htmltag.tr(htmltag.td(key), htmltag.td(str(value)))
        trs.append(tr)
    tbody = htmltag.tbody(*trs)
    return htmltag.table(thead, tbody)


def pagebreak():
    """ create a page break (will show up when printing to pdf) """
    return htmltag.div('', style = "page-break-after:always;")


def plot(plotSpec):
    """ create a plot by storing the data in a json file and returning HTML for displaying the plot """
    global nextPlotIndex
    
    # compute an ID for this plot
    id = 'plot%d' % nextPlotIndex
    nextPlotIndex += 1
    
    # make a copy of the plot spec (except data) so that we can re-generate a report without regenerating the plot specs
    # (converting the data frames will take place only in this copy)
    dataSpecs = plotSpec.get('data', [])
    plotSpec = {k:v for (k,v) in plotSpec.items() if k != 'data'} # copy all but data
    plotSpec['data'] = []
    
    # get original value for timestamp type
    timeX = (plotSpec.get('typeX', 'none') == 'timestamp')
    
    # convert data frames
    for dataSpec in dataSpecs:
    
        # check for timestamp index
        df = dataSpec['df']
        timeDf = df.index.dtype == 'datetime64[ns]'
        if timeX and not timeDf:
            raise Exception( 'typeX is timestamp but df has non-timestamp index' )
        if timeDf:
            timeX = True
        
        # create new data spec with df converted to dict/lists for json
        newDataSpec = {k:v for (k,v) in dataSpec.items() if k != 'df'} # copy all but df
        newDataSpec['df'] = dataFrameToDict(df)
        plotSpec['data'].append(newDataSpec)
        
        # check timestamps
     
    # set timestamp type
    if timeX:
        plotSpec['typeX'] = 'timestamp'
            
    # check for out-of-date API calls
    for dataSpec in dataSpecs:
        if 'format' in dataSpec:
            print 'warning: format in data spec no longer supported'

    # create HTML
    h = htmltag.div('', id = id)
    h += htmltag.script('var g_%s = %s;\ngeneratePlot("%s", g_%s);' % (id, json.dumps(plotSpec), id, id))
    return h


def save(html, title, outputFileName):
    """ save HTML output; copies files into the directory containing the output file """
    global nextPlotIndex
    
    # the HTML library (css/js) path is relative to this module
    libPath = os.path.dirname(__file__)
    
    # create output directory if needed
    outputPath = os.path.dirname(outputFileName)
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    
    # copy files referenced by HTML file into output directory
    sourcePath = libPath + '/htmlLibs'
    fileNames = os.listdir(sourcePath)
    for fileName in fileNames:
        shutil.copy(sourcePath + '/' + fileName, outputPath + '/' + fileName)
    
    # fill the template
    templateContents = open(libPath + '/template.html').read()
    template = jinja2.Template(templateContents)
    html = template.render(title = title, contents = str(html))
    
    # save the html file to disk
    open(outputFileName, 'w').write(html)
    
    # reset the plot counter
    nextPlotIndex = 1


def table(df, lastRowIsFooter=False, format=None):
    """ generate an HTML table from a pandas data frame """
    if not format:
        format = {}
    rowCount = len(df)
    
    # default column formatting
    defaultFormat = {
        'align': 'right',
        'decimalPlaces': 2,
        'commas': True,
    }
    
    # a helper function to get column formatting
    def getFormat(colName, attribute):
        if colName in format and attribute in format[colName]:
            value = format[colName][attribute]
        elif '*' in format and attribute in format['*']:
            value = format['*'][attribute]
        else:
            value = defaultFormat[attribute]
        return value
    
    # create header
    first = True
    items = []
    for colName in df.columns:
        if getFormat(colName, 'align') == 'right':
            items.append(htmltag.th(colName, _class='alignRight'))
        else:
            items.append(htmltag.th(colName))
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
            colName = df.columns[j]
            if isNumeric(v):
                decimalPlaces = getFormat(colName, 'decimalPlaces')
                if getFormat(colName, 'commas'):
                    pattern = '{:,.' + str(decimalPlaces) + 'f}'
                else:
                    pattern = '{:.' + str(decimalPlaces) + 'f}'
                v = pattern.format(v)
            if getFormat(colName, 'align') == 'right':
                items.append(htmltag.td(v, _class='alignRight'))
            else:
                items.append(htmltag.td(v))
            first = False
        if lastRowIsFooter and i == rowCount - 1:
            tfoot = htmltag.tfoot(htmltag.tr(*items))
        else:
            rows.append(htmltag.tr(*items))
    tbody = htmltag.tbody(*rows)
    return htmltag.table(thead, tbody, tfoot)


# ======== utility functions ========


def dataFrameToDict(df):
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


def isNumeric(v):
    """ check whether a value is numeric (could be float, int, or numpy numeric type) """
    return hasattr(v, '__sub__') and hasattr(v, '__mul__')
