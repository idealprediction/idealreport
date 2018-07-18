# idealreport
Ideal Prediction reporting framework

Idealreport translates data from pandas DataFrames to HTML presentations, including plots, tables, and text.  The HTML is rendered using javascript libraries based on D3.js so the resulting graphs are aesthetically pleasing.

### Install
Pip is the easiest install method.  The module is built as a python wheel so it easily works across various OSs.
```
pip install idealreport
```

### Dependencies
* required: htmltag (requires sphinx), pandas 
* recommended: phantomjs to generate PDFs from HTML
```
pip install sphinx, htmltag, pandas
```

### Examples
See ```sample_plots.py``` for examples of how to create plots using the Reporter class (inputs pandas DataFrames and outputs python dictionaries of plot specifications) and create_html (inputs python dictionaries of plot specifications).

This example uses the Reporter class to create an HTML file with a single plot:

```
from datetime import datetime
import os
import htmltag
import idealreport
import pandas as pd

# example P+L data - note: plots will use the index as the x axis 
df = pd.DataFrame(data={'time': [datetime(2016, 2, 3, 10, 0, 0), datetime(2016, 2, 3, 11, 0, 0), datetime(2016, 2, 3, 12, 0, 0)],
                    'P+L': [80, -20, 45]})
df = df.set_index('time')

# instantiate the Reporter class and specify the title and output location
output_path = '.'
r = idealreport.Reporter(title='Report', output_file=os.path.join(output_path, 'report.html'))

# title
r.h += htmltag.h4('Example report')

# bar plot 
r.h += r.plot.bar(df=df, title='Hourly P+L', y_label='$k')

# render to HTML
r.generate()
```
