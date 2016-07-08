import htmltag
from idealreport import createhtml

class Plotter(object):
    """ Class to wrap report plotting """

    def __init__(self, reporter):
        """ store the Reporter instance to allow adding HTML to the report stored internally in Reporter"""
        self.reporter = reporter

    def _addLabels(self, plotDict, title, xLabel=None, yLabel=None):
        """ add standard labels to a plot dictionary - title is required """
        plotDict['title'] = title
        if xLabel is not None:
            plotDict['x'] = {'label': xLabel}
        if yLabel is not None:
            plotDict['y'] = {'label': yLabel}
        return plotDict

    def bar(self, df, title, xLabel=None, yLabel=None, stacked=False, horizontal=False):
        """  plot a df as a bar plot 
            Args:
                df (DataFrame)
                title, xLabel, yLabel (str): title is required and others are optional
        """

        # stacked vs normal bar plots
        plotType = 'bar'
        if stacked:
            plotType = 'stackedBar'

        # vertical vs horizontal bars
        orientation = 'v'
        if horizontal:
            orientation = 'h'

        # dict() to store info for plotting
        plotDict = {
            'data': [{'df': df, 'type': plotType, 'orientation': orientation, 'staticPlot': False}]
        }

        # plot labels + create HTML
        plotDict = self._addLabels(plotDict, title, xLabel, yLabel)
        self.reporter.h += createhtml.plot(plotDict)

    def barh(self, df, title, xLabel=None, yLabel=None, stacked=False):
        """  plot a df as a horizontal bar plot 
            Args:
                df (DataFrame)
                title, xLabel, yLabel (str): title is required and others are optional
        """
        self.bar(df, title, xLabel, yLabel, stacked, horizontal=True)

    def time(self, df, title, gapTimeFmt=None, xLabel=None, yLabel=None):
        """ plot a df as a timeseries 
            Args:
                df (DataFrame)
                gapTimeFmt (str): If specified, then skip gaps and format timestamps using this str
                title, xLabel, yLabel (str): title is required and others are optional
        """
        # remove nan and replace timestamps as strings to handle gaps in time
        if gapTimeFmt is not None:
            isOneDim = (len(df.shape) == 1) or (df.shape[1] == 1)
            #print df.shape, isOneDim            
            if isOneDim:
                df = df[df.notnull()]
            else:
                df = df[df.notnull().any(axis=1)]
            df.index = df.index.map(lambda dt: dt.strftime(gapTimeFmt))

        # dict() to store info for plotting
        plotDict = {
            'data': [{'df': df, 'type': 'line'}],
        }

        # plot labels + create HTML
        plotDict = self._addLabels(plotDict, title, xLabel, yLabel)
        self.reporter.h += createhtml.plot(plotDict)


class Reporter(object):
    """ class to wrap the report class and add helper f()s - perhaps push functionality to the report class? """
    def __init__(self, title, outputFile):
        self.title = title
        self.outputFile = outputFile
        # html string
        self.h = ''  
        # wrapper for plots, including a reference to this reporter instance to store HTML
        self.plotter = Plotter(self)
        
    def addPageBreak(self):
        self.h += createhtml.pagebreak()
        
    #def plot(self):
    #    return self.plotWrap

    def _addPlotLabels(self, plotDict, title, xLabel=None, yLabel=None):
        """ add standard labels to a plot dictionary - title is required """
        plotDict['title'] = title
        if xLabel is not None:
            plotDict['x'] = {'label': xLabel}
        if yLabel is not None:
            plotDict['y'] = {'label': yLabel}
        return plotDict
                
    def addText(self, text):
        self.h += htmltag.p(text)

    def filterStr(startList, filterList):
        """ find all the items in startList that have a substr within filterList
        endList: all items in startList that have matches
        diffList: the difference between startList and endList (used for future f() calls)
        """
        #return [x for x in startList if f in x for f in filterList]
        endList = []
        for f in filterList:
            endList.extend([x for x in startList if f in x])
        return endList, list(set(startList) - set(endList))
        
    def generate(self):
        """ generate and save the report HTML """
        createhtml.save(self.h, self.title, self.outputFile)
        print 'saved report to %s' % self.outputFile

    