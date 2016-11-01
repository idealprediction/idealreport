# idealreport
Ideal Prediction reporting framework

Idealreport translates data from pandas DataFrames to HTML presentations, including plots, tables, and text.  The HTML is rendered using javascript libraries based on D3.js so the resulting graphs are aesthetically pleasing.

### Install
Pip is the easiest install method.  The module is built as a python wheel so it easily works across various OSs.
```
pip install idealreport
```

### Dependencies
requires: htmltag (requires sphinx), pandas 

recommended: phantomjs

### Example
```
from datetime import datetime
import os
import htmltag
from idealreport.reporter import Reporter
from pandas import DataFrame

# example P+L data - note: plots will use the index as the x axis 
df = DataFrame(data={'time': [datetime(2016, 2, 3, 10, 0, 0), datetime(2016, 2, 3, 11, 0, 0), datetime(2016, 2, 3, 12, 0, 0)],
                    'P+L': [80, -20, 45]})
df = df.set_index('time')

# instantiate the Reporter class and specify the title and output location
outputDir = '.'
r = Reporter(title='Report', output_file=os.path.join(outputDir, 'report.html'))

# Title
r.h += htmltag.h4('Example report')
# bar plot 
r.plot.bar(df=df, title='Hourly P+L', ylabel='$k')

# render to HTML
r.generate()
```
