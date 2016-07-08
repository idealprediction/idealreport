var g_autoLegendGroupId = 1;


function generatePlot(id, plotSpec) {
	var plotDiv = document.getElementById(id);
	
	// common to all plot types
	if (!plotSpec.margin) {
		plotSpec.margin = {};
	}
	if (!plotSpec.margin.l) {
		plotSpec.margin.l = 50;
	}
	
	// generate the plot
	if (plotSpec.type === 'heatMap') {
		generateHeatMap(plotDiv, plotSpec);
	} else {
		generateGenericPlot(plotDiv, plotSpec);
	}
}


function generateGenericPlot(plotDiv, plotSpec) {
	
	// default layout: copy any attributes from axis spec
	var layout = { xaxis: {}, yaxis: {} /*, margin: { t: 0, r: 0 } */ };
	if (plotSpec.x) {
		layout.xaxis = plotSpec.x;
	}
	if (plotSpec.y) {
		layout.yaxis = plotSpec.y;
	}
	if (plotSpec.y2) {
		layout.y2axis = plotSpec.y2;
	}
	if (plotSpec.legend) {
		layout.legend = plotSpec.legend;
	}
	if (plotSpec.height) {
		layout.height = plotSpec.height;
	}
	
	// create data object
	var data = [];
	for (var i = 0; i < plotSpec.data.length; i++) {
		var dataSpec = plotSpec.data[i];
		var columns = dataSpec.df;
		
		// increment legend group (even if we're not going to use it)
		g_autoLegendGroupId++;
		
		// loop over columns in data frame
		for (var j = 1; j < columns.length; j++) {
			var column = columns[j];
			var dataItem = {
				x: columns[0].values,
				y: columns[j].values,
				name: column.name,
			}; // fix(soon): initialize dataItem with copy of dataSpec so no need to copy individual attributes
			if (dataSpec.name) { 
				dataItem.name = dataSpec.name;
			}
			
			// if error bars, add them
			if (dataSpec.errorBars) {
				var errorInfo = {
					type: 'data',
					array: columns[2].values,
					visible: true
				};
				if (dataSpec.errorBars.symmetric === false) {
					errorInfo.symmetric = false;
					errorInfo.arrayminus = columns[3].values;
				}
				j = columns.length; // skip rest of columns for this data frame
				if (dataSpec.orientation == 'h') {
					dataItem.error_x = errorInfo;
				} else {
					dataItem.error_y = errorInfo;
				}
			}
			
			// get formatting from data spec
			dataItem.orientation = dataSpec.orientation;
			dataItem.mode = dataSpec.mode;
			dataItem.fillcolor = dataSpec.fillcolor;
			dataItem.legendgroup = dataSpec.legendgroup;
			if (dataSpec.type !== 'line') {
				dataItem.type = dataSpec.type;
			}
			
			// handle continuous error bars
			if (dataSpec.type === 'continuousErrorBars') {
				if (!dataItem.legendgroup) {
					dataItem.legendgroup = 'lg' + g_autoLegendGroupId;
				}
				if (j == 2) {
					var means = columns[1].values;
					var devs = columns[2].values;
					var upper = [];
					var lower = [];
					for (var k = 0; k < dataItem.x.length; k++) {
						upper.push(means[k] + devs[k]);
						lower.push(means[k] - devs[k]);
					}
					dataItem.y = upper;
					dataItem.fill = "tonexty";
					dataItem.line = {color: "transparent"};
					dataItem.showlegend = false;
					dataItem.type = "scatter";

					// make a copy for the lower bound
					var newDataItem = {};
					Object.keys(dataItem).forEach(function(key) {
						 newDataItem[key] = dataItem[key];
					}); 
					newDataItem.fill = null;
					newDataItem.y = lower;
					data.push(newDataItem);
					
				// handle mean line of continuous error bars
				} else {
					dataItem.type = "scatter";
					dataItem.mode = "lines";
				}
			}
			
			// handle second y axis
			if (dataSpec.y2) {
				dataItem.yaxis = 'y2';
				layout.yaxis2 = {
					title: plotSpec.labelY2,
					overlaying: 'y',
					side: 'right'
				};
			}
			
			// handle horizontal bar chart: swap x and y
			if (dataItem.orientation === 'h') {
				var x = dataItem.x;
				dataItem.x = dataItem.y;
				dataItem.y = x;
			}
			
			// handle 2d histograms
			if (dataItem.type === 'histogram2d') {
				if (plotSpec.x && plotSpec.x.bins) {
					dataItem.xbins = plotSpec.x.bins;
				}
				if (plotSpec.y && plotSpec.y.bins) {
					dataItem.ybins = plotSpec.y.bins;
				}
			}
			
			// provide a default mode for scatter plots
			if (dataItem.type === 'stackedBar') {
				dataItem.type = 'bar';
				layout.barmode = 'stack';
			}
			
			// provide a default mode for scatter plots
			if (dataItem.type === 'scatter' && !dataItem.mode && dataSpec.type !== 'continuousErrorBars') {
				dataItem.mode = 'markers';
			}
			data.push(dataItem);
		}
		
		// handle histograms
		if (dataSpec.type === 'histogram') {
			var dataItem = JSON.parse(JSON.stringify(dataSpec)); // make copy; assumes just simple data
			dataItem.x = columns[0].values;
			dataItem.name = dataSpec.name || columns[0].name; // use column name if no spec name specified
			data.push(dataItem);
		}
	}
	
	// handle timestamps
	if (plotSpec.typeX === 'timestamp') {
		for (var i = 0; i < data.length; i++) {
			var x = data[i].x;
			console.log(x);
			var newX = [];
			var len = x.length;
			for (var j = 0; j < len; j++) {
				newX[j] = Date.parse(x[j]);
			}
			layout.xaxis.type = 'date'
			data[i].x = newX;
			console.log(newX);
		}
	}
	
	// old code for axis formatting
	// fix(clean): remove this
	if (plotSpec.labelX) {
		layout.xaxis.title = plotSpec.labelX;
	}
	if (plotSpec.labelY) {
		layout.yaxis.title = plotSpec.labelY;
	}
	if (plotSpec.rangeX !== undefined) {
		layout.xaxis.range = plotSpec.rangeX;
	}
	if (plotSpec.rangeY !== undefined) {
		layout.yaxis.range = plotSpec.rangeY;
	}
	if (plotSpec.rangeY2 !== undefined && layout.yaxis2) {
		layout.yaxis2.range = plotSpec.rangeY2;
	}
	if (plotSpec.zeroLineX !== undefined) {
		layout.xaxis.zeroline = plotSpec.zeroLineX;
	}
	if (plotSpec.zeroLineY !== undefined) {
		layout.yaxis.zeroline = plotSpec.zeroLineY;
	}
	if (plotSpec.zeroLineY2 !== undefined && layout.yaxis2) {
		layout.yaxis2.zeroline = plotSpec.zeroLineY2;
	}
	
	// a helper function for access attributes
	function processAxis(axisSpec, layoutAxis) {
		if (axisSpec.label !== undefined) { 
			layoutAxis.title = axisSpec.label;
		}
		if (axisSpec.range !== undefined) { // fix(clean): probably not needed now that we init with axis spec
			layoutAxis.range = axisSpec.range; 
		}
		if (axisSpec.zeroLine !== undefined) { 
			layoutAxis.zeroline = axisSpec.zeroLine;
		}
		if (axisSpec.hoverFormat !== undefined) { 
			layoutAxis.hoverformat = axisSpec.hoverFormat;
		}
	}
	
	// process axis attributes
	// fix(clean): move up to top
	if (plotSpec.x) {
		processAxis(plotSpec.x, layout.xaxis);
	}
	if (plotSpec.y) {
		processAxis(plotSpec.y, layout.yaxis);
	}
	if (plotSpec.y2) {
		processAxis(plotSpec.y2, layout.yaxis2);
	}
	
	// other layout
	if (plotSpec.title) {
		layout.title = plotSpec.title;
	}
	if (plotSpec.margin) {
		layout.margin = plotSpec.margin;
	}
	
	// determine whether to include interactive elements
	var staticPlot = true;
	if (plotSpec.staticPlot !== undefined) {
		staticPlot = plotSpec.staticPlot;
	}
	
	// create the plot
	Plotly.newPlot(plotDiv, data, layout, {staticPlot: staticPlot});
}


function generateHeatMap(plotDiv, plotSpec) {

	// create data object
	var data = [
		{
			type: 'heatmap',
			x: plotSpec.rangeX,
			y: plotSpec.rangeY,
			z: plotSpec.z,
		}
	];
	
	// create layout object
	var layout = { 
		xaxis: { 
		}, 
		yaxis: { 
		}
	};
	if (plotSpec.title) {
		layout.title = plotSpec.title;
		if (plotSpec.labelX)
			layout.xaxis.title = plotSpec.labelX;
		if (plotSpec.labelY)
			layout.yaxis.title = plotSpec.labelY;
	}
	if (plotSpec.margin) {
		layout.margin = plotSpec.margin;
	}
	
	// determine whether to include interactive elements
	var staticPlot = true;
	if (plotSpec.staticPlot !== undefined) {
		staticPlot = plotSpec.staticPlot;
	}

	// create the plot
	Plotly.newPlot(plotDiv, data, layout, {staticPlot: staticPlot});
}
