# This example script shows how to utilize idealreport to create various interactive HTML plots.
# The framework generates a "report" that is an HTML file with supporting js files.
#
# These are the steps to generate the example report:
# 1. Use python 2.7 and install the requirements using "pip install htmltag pandas"
# 2. Run this script "python sample_plots.py" 
# 3. Open the resulting HTML file in a browswer "reports/sample_plots.html"
# 
# This sample shows how to utilize the framework via:
# (1) create_html.py functions in create_html.py 
# (2) report.py Reporter class in report.py which wraps functions in (1)
# The create_html functions are more general, but often require more verbose code.
# 
# abbreviations in the comments:
# - df = a pandas DataFrame
# - ps = plot specification (python dictionary) used by create_html

import os
import htmltag
import idealreport as ir
import numpy as np
import pandas as pd

# data stored in pandas DataFrames (df)
# df: bar charts
df_bar = pd.DataFrame({'Stat 1': [2.0, 1.6, 0.9, 0.2, -1.3],
    'Stat 2': [1.1, 0.7, -0.8, -1.4, 0.4],
    'Value 1': [8, 10, 50, 85, 42],
    'Value 2': [100, 50, 10, 100, 25]
    }, index=['Entity 1', 'Entity 2', 'Entity 3', 'Entity 4', 'Entity 5'])

# df: line, scatter, mixed (e.g. line and bar), secondary Y-axis, box
df_line = pd.DataFrame({'a': np.arange(0, 20) - 8, 'b': -2 * np.arange(0, 20) + 5})
df_line['b'] = df_line['b'] + np.random.randn(20)

# df: line with error
df_error = df_line.copy()
df_error['error 1'] = df_error['a'].abs() * 0.2
df_error['error 2'] = df_error['b'].abs() * 0.4
df_error.set_index('a', inplace=True)

# df: open high low close (OHLC)
df_ohlc = pd.DataFrame(np.random.randn(20, 4), columns=['open', 'high', 'low', 'close'])
df_ohlc['high'] = df_ohlc['high'] + 3
df_ohlc['low'] = df_ohlc['low'] - 3

# df: Sankey
df_sankey = pd.DataFrame(np.array([[0,2,8], [1,3,4], [0,3,2], [2,3,8], [3,4,4], [3,5,2]]))
df_sankey.columns = ['source', 'target', 'value']

# plot specifications (ps) used by create_html
# ps: vertical bar chart (additional data field required: orientation)
bar_plot = {
    'title': 'Vertical Bar Chart (Create HTML)',
    'data': [
        {
            'df': df_bar[['Stat 1', 'Stat 2']],
            'type': 'bar',
            'orientation': 'v',
        },
    ],
    'labelX': 'Entity',
    'labelY': 'Stat',
    'staticPlot': False
}

# ps: stacked horizontal bar chart (additional data field required: orientation)
stacked_bar_plot = {
    'title': 'Horizontal Stacked Bar Chart (Create HTML)',
    'data': [
        {
            'df': df_bar[['Value 1', 'Value 2']],
            'type': 'stackedBar',
            'orientation': 'h',
        },
    ],
    'labelX': 'Value',
    'staticPlot': False
}

# ps: line chart
line_plot = {
    'title': 'Line Plot (Create HTML)',
    'data': [
        {
            'df': df_line,
            'type': 'line',
        },
    ],
    'staticPlot': False
}

# ps: scatter plot
scatter_plot = {
    'title': 'Scatter Plot (Create HTML)',
    'data': [
        {
            'df': df_line.set_index('a'),
            'type': 'scatter',
        },
    ],
    'labelX': 'alpha',
    'labelY': 'beta',
    'staticPlot': False
}

# ps: mixed plot types on one graph
multi_scatter_plot = {
    'title': 'Mixed Line and Bar Plot (Create HTML)',
    'data': [
        {
            'df': df_line['a'],
            'type': 'line',
        },
        {
            'df': df_line['b'],
            'type': 'bar',
            'orientation': 'v',
        },
    ],
    'labelX': 'x label',
    'labelY': 'y label',
    'staticPlot': False
}

# ps: secondary Y-axis
multi_axis_plot = {
    'type': 'line',
    'title': 'Secondary Y-Axis Plot (Create HTML)',
    'data': [
        {
            'df': df_line['a'],
            'type': 'line',
        },
        {
            'df': df_line['b'],
            'type': 'line',
            'y2': True,
        },
    ],
    'labelX': 'x',
    'labelY': 'y from a',
    'labelY2': 'y from b',
}

# ps: box plot
box_plot = {
    'title': 'Box Plot (Create HTML)',
    'data': [
        {
            'df': df_line,
            'orientation': 'v',
        },
    ],
    'type': 'box',
    'staticPlot': False,
}

# ps: sankey plot
sankey_plot = {
    'title': 'Sankey Plot (Create HTML)',
    'data': [
        {
            'df': df_sankey,
        },
    ],
    'nodeLabels': ['node_a', 'node_b', 'node_c', 'node_d', 'node_e', 'node_f'],
    'linkLabels': ['Link_a', 'link_b', 'link_c', 'link_d', 'link_e', 'link_f'],
    'type': 'sankey',
    'staticPlot': False
}

# report: instantiate the Reporter class, specifying the output path and file name
output_path = 'reports/'
output_file = os.path.join(output_path, 'sample_plots.html')
r = ir.Reporter(title='Sample Plots', output_file=output_file)

# report: title and introduction
# note: html tag generates HTML which we can append to the report "h" attribute
r.h += htmltag.h3('Sample Ideal Report')
r.h += htmltag.text('This report illustrates how to generate an HTML report with various plot types.\n')
r.h += htmltag.text('Many plots are generated by create_html functions with a plot specification (Create HTML) ')
r.h += htmltag.text('as well as the Reporter class (Reporter).')

# report: bar charts
r.h += htmltag.h4('Bar Charts')
r.h += r.plot.bar(df=df_bar[['Stat 1', 'Stat 2']], title='Vertical Bar Chart (Reporter)', x_label='Entity', y_label='Stats')
r.h += ir.create_html.plot(bar_plot)
r.h += r.plot.bar(df=df_bar[['Value 1', 'Value 2']], title='Horizontal Stacked Bar Chart (Reporter)', horizontal=True, stacked=True, x_label='Values')
r.h += ir.create_html.plot(stacked_bar_plot)

# report: bar chart, specifying colors for the bars
markers = [{'color': 'rgb(59, 115, 186)'}, {'color': 'rgb(185, 187, 211)'}]
r.h += r.plot.bar(df=df_bar[['Stat 1', 'Stat 2']], title='Vertical Bar Chart with Colors (Reporter)', x_label='Entity', y_label='Stats', custom_design={'markers': markers})

# report: overlay bar chart, specifying width and opacity of the bars
# widths = [.4, .2]
# opacities = [.6, 1]
custom_design = {'markers': markers, 'opacities': [0.6, 1.0], 'widths': [0.4, 0.2]}
r.h += r.plot.baroverlay(df=df_bar[['Value 1', 'Value 2']], title='Vertical Overlay Bar Chart (Reporter)', orientation='v', x_label='$', custom_design=custom_design)

# report: histogram
r.h += r.plot.histogram(df=df_line, title='Histogram (Reporter)', y_label='Observations', custom_design={'markers': markers})

# report: pie and donut (i.e. pie with a hole in the center)
r.h += r.plot.pie(df=df_bar, title='Pie Chart (Reporter)')
r.h += r.plot.pie(df=df_bar, title='Donut (Reporter)', hole=.4)

# report: line plots
r.h += htmltag.h4('Line Plots')
r.h += r.plot.line(df=df_line, title='Line Plot (Reporter)', x_label='Entity', y_label='Value')
r.h += ir.create_html.plot(line_plot)

# report: line plot, specifying width and color
lines = [{'width': 7, 'color': 'rgb(59, 115, 186)'}, {'width': 3, 'color': 'rgb(185, 187, 211)'}]
r.h += r.plot.line(df=df_line, title='Line Plot with Width and Color', x_label='Entity', y_label='Value', custom_design={'lines': lines})

# report: points with error bar
# note: only first 3 columns are used for symmetric error bars
r.h += r.plot.errbar(df=df_error, title='Points with Symmetric Error Bars (Reporter)')
r.h += r.plot.errbar(df=df_error, title='Points with Asymmetric Error Bars (Reporter)', symmetric=False)

# report: line with error 
r.h += r.plot.errline(df=df_error[['b', 'error 2']], title='Symmetric Error Lines (Reporter)')

# report: time series line
df = df_line.copy()
df['time'] = pd.date_range('2017-11-02 9:00', periods=len(df), freq='T') 
df.set_index('time', inplace=True)
r.h += r.plot.line(df=df, title='Time Series', x_label='Time', y_label='Value')

# report: OHLC
r.h += htmltag.h4('Open High Low Close (OHCL) Plot')
r.h += r.plot.ohlc(df=df_ohlc, title='OHLC Plot (Reporter)', x_label='price', y_label='instrument')

# report: scatter plots
r.h += htmltag.h4('Scatter Plots')
r.h += r.plot.scatter(df=df_line.set_index('a'), title='Scatter Plot (Reporter)', x_label='alpha', y_label='beta')
r.h += ir.create_html.plot(scatter_plot)

# report: scatter plot with a custom layout
layout = {
    'font': {'family':'Arial', 'color':'#77797c'},
    'xaxis': {'showgrid': False, 'showline': False, 'zerolinecolor': '#acadaf', 'ticks': 'outside', 'tickcolor': '#acadaf', 'hoverformat': '.2f'},
    'yaxis': {'showgrid': False, 'zeroline': True, 'showline': False, 'zerolinecolor': '#acadaf', 'linewidth': 10, 'ticks': '', 'tickcolor': '#acadaf', 'hoverformat': '.2f'},
    'width': 500,
    'height': 500,
    'showlegend': False
}
custom_design = {'layout': layout, 'markers': markers}
r.h += r.plot.scatter(df=df_line.set_index('a'), title='Scatter Plot Custom Layout (Reporter)', x_label='alpha', y_label='beta', custom_design=custom_design)

# report: scatter plot with a custom layout / shape
layout = {
    'font': {'family':'Arial', 'color':'#77797c'},
    'xaxis': {'showgrid': False, 'showline': False, 'zerolinecolor': '#acadaf', 'ticks': 'outside', 'tickcolor': '#acadaf', 'hoverformat': '.2f'},
    'yaxis': {'showgrid': False, 'zeroline': True, 'showline': False, 'zerolinecolor': '#acadaf', 'linewidth': 10, 'ticks': '', 'tickcolor': '#acadaf', 'hoverformat': '.2f'},
    'width': 500,
    'height': 500,
    'shapes': [{'type': 'line', 'xref': 'paper', 'yref': 'paper', 'x0': 0, 'y0': 0,
        'x1': 0.5, 'y1': 0.5, 'line': {'color': 'rgb(50, 171, 96)', 'width': 3}}],
    'showlegend': False
}
custom_design = {'layout': layout, 'markers': markers}
r.h += r.plot.scatter(df=df_line.set_index('a'), title='Scatter Plot Custom Layout / Shape (Reporter)', x_label='alpha', y_label='beta', custom_design=custom_design)

# report: mixed plot types
r.h += htmltag.h4('Multi Series, Mixed Type Plots')
r.h += r.plot.multi(dfs=[df_line['a'], df_line['b']], types=['line', 'bar'], title='Mixed Line and Bar Plot (Reporter)', x_label='x label', y_label='y label')
r.h += ir.create_html.plot(multi_scatter_plot)

# report: secondary Y-axis
r.h += r.plot.multi(dfs=[df_line['a'], df_line['b']], types=['line', 'line'], title='Secondary Y-Axis (Reporter)', x_label='x', y_label='y from a', y2_axis=[False, True], y2_label='y from b')
r.h += ir.create_html.plot(multi_axis_plot)

# report: univariate
# note: use data_static to specify attributes that are the same across each trace
df = pd.DataFrame(np.random.randn(1,5), columns=['a', 'b', 'c', 'd', 'e'])
layout = {
    'xaxis': {'autorange': True, 'showgrid': False, 'showline': False, 'zerolinecolor': '#acadaf', 'ticks': '', 'tickcolor': '#acadaf', 'showticklabels': True},
    'yaxis': {'autorange': True, 'showgrid': False, 'zeroline': True, 'showline': False, 'zerolinecolor': '#acadaf', 'autotick': False, 'linewidth': 10, 'showticklabels': False},
    'width': 500,
    'height': 250,
    'showlegend': False,
}
data_static = {'mode': 'markers+text', 'orientation': 'h', 'textposition': 'top',}
data_to_iterate = {'text': ['a', 'b', 'c', 'd', 'e']}
custom_data = {'data_static': data_static, 'data_to_iterate': data_to_iterate}
r.h += r.plot.scatter(df=df, title='Horizontal Univariate Plot', x_label='alpha', custom_data=custom_data, custom_design={'layout': layout})

# report: box plot
r.h += htmltag.h4('Box Plots')
r.h += r.plot.box(df=df_line, title='Box Plot (Reporter)', horizontal=False)
r.h += ir.create_html.plot(box_plot)

# report: sankey plot
r.h += htmltag.h4('Sankey Plots')
r.h += r.plot.sankey(df=df_sankey, title='Sankey Plot (Reporter)', 
    custom_design={'nodeLabels': ['node_a', 'node_b', 'node_c', 'node_d', 'node_e', 'node_f']})
r.h += ir.create_html.plot(sankey_plot)

# report: generate and save the HTML
r.generate()