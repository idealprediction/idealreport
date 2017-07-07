import time
import random
import datetime
import os
from pandas import DataFrame, to_datetime, DatetimeIndex
import numpy as np
import idealreport.create_html as ch
from idealreport.reporter import Reporter
import htmltag

dfhb = DataFrame({'Entity': ['Entity 1', 'Entity 2', 'Entity 3', 'Entity 4', 'Entity 5'],
                  'Stat 1': np.random.randn(5).tolist(),
                  'Stat 2': np.random.randn(5).tolist(),
                 })
dfhb = dfhb.set_index('Entity')
dfhb = dfhb.sort_values(by='Stat 1', ascending=False)

bar_plot = {
    'title': 'Sample Bar Chart by Create HTML',
    'data': [
        {
            'df': dfhb,
            'type': 'bar',
            'orientation': 'v',
        },
    ],
    'labelX': 'Entity',
    'labelY': '%',
    'staticPlot': False
}

dfsb = DataFrame({'Entity': ['Entity 1', 'Entity 2', 'Entity 3', 'Entity 4', 'Entity 5'],
                'Foo': [8, 10, 50, 85, 42],
                'Bar': [100, 50, 10, 100, 25]})
dfsb = dfsb.set_index('Entity')
dfsb = dfsb[['Foo', 'Bar']] # make sure columns have desired order

stacked_bar_plot = {
    'title': 'Sample Stacked Bar Chart by Create HTML',
    'data': [
        {
            'df': dfsb,
            'type': 'stackedBar',
            'orientation': 'h',
        },
    ],
    'labelX': '$',
    'staticPlot': False
}

dfsp = DataFrame(np.random.randn(20, 2))
dfsp.columns = ['a', 'b']
dfsp = dfsp.set_index('a')
scatter_plot = {
    'title': 'Sample Scatter Plot by Create HTML',
    'data': [
        {
            'df': dfsp,
            'type': 'scatter',
        },
    ],
    'labelX': 'alpha',
    'labelY': 'beta',
    'staticPlot': False
}

df1 = DataFrame(np.random.randn(200, 2))
df1.columns = ['a', 'b1']
df1 = df1.set_index('a')
df2 = DataFrame(np.random.randn(200, 2))
df2.columns = ['a', 'b2']
df2 = df2.set_index('a')
df3 = DataFrame(np.random.randn(200, 2))
df3.columns = ['a', 'b3']
df3 = df3.set_index('a')
multi_scatter_plot = {
    'title': 'Sample Scatter Plot with Multiple Series by Create HTML',
    'data': [
        {
            'df': df1,
            'type': 'scatter',
        },
        {
            'df': df2,
            'type': 'scatter',
        },
        {
            'df': df3,
            'type': 'scatter',
        },
    ],
    'labelX': 'x label',
    'labelY': 'y label',
}

output_path = '/home/jason/ideal/reports/sample_report/output'
output_file = os.path.join(output_path, 'sample_plots.html')
r = Reporter(title='Sample Plots', output_file=output_file)

# report start
r.h += htmltag.h3('This report illustrates some additional plotting types.')

# bar charts
r.h += htmltag.h4('Bar Charts')
r.plot.bar(df=dfhb, title='Sample Bar Chart by Reporter', xlabel='Entity', ylabel='%')
r.h += ch.plot(bar_plot)
r.plot.barh(df=dfsb, title='Sample Stacked Bar Chart by Reporter', stacked=True, xlabel='$')
r.h += ch.plot(stacked_bar_plot)

# scatter plots
r.h += htmltag.h4('Scatter Plots')
r.plot.scatter(df=dfsp, title='Sample Scatter Plot by Reporter', xlabel='alpha', ylabel='beta')
r.h += ch.plot(scatter_plot)
r.plot.multi(dfs=[df1, df2, df3], types=['scatter', 'scatter', 'scatter'], title='Sample Scatter Plot with Multiple Series by Reporter', xlabel='alpha', ylabel='beta')
r.h += ch.plot(multi_scatter_plot)

# generate and save the report HTML
r.generate()