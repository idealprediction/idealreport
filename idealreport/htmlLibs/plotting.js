var g_autoLegendGroupId = 1;


function generatePlot(id, plotSpec) {
	var plotDiv = document.getElementById(id);
	
	// common to all plot types
	/*if (plotSpec.layout == undefined) {
		plotSpec.margin = {};

	} else if (plotSpec.layout.margin == undefined) {
		plotSpec.margin = {l: 50};
		//plotSpec.margin.l = 50;
	} else if (plotSpec.layout.margin.l == undefined) {
		plotSpec.margin.l = 50;
	}*/
	
	// generate the plot
	if (plotSpec.type === 'heatMap') {
		generateHeatMap(plotDiv, plotSpec);
	} else if (plotSpec.type === 'sankey') {
		generateSankeyPlot(plotDiv, plotSpec);
	} else if (plotSpec.type === 'box') {
		generateBoxPlot(plotDiv, plotSpec);
	} else if (plotSpec.type === 'cubism') {
		generateCubismPlot(plotDiv, plotSpec);
	} else {
		generateGenericPlot(plotDiv, plotSpec);
	}
}


function generateGenericPlot(plotDiv, plotSpec) {
	
	let layout;

	// default layout with xaxis and yaxis set to empty dicts and margin.l set to 50 if not specified in plotSpec.layout
	if (plotSpec.layout) {
		layout = plotSpec.layout;
		// fill in required values if they're missing
		if (!layout.xaxis) {
			layout.xaxis = {};
		}
		if (!layout.yaxis) {
			layout.yaxis = {};
		}
		if (!layout.margin) {
			layout.margin = {};
			layout.margin.l = 50;
		} else if (!layout.margin.l) {
			layout.margin.l = 50;
		}
	} else {
		layout = {xaxis: {}, yaxis: {}, margin: {l: 50}};
	}

	// leaving title, xaxis and yaxis as params for reporter for basic charts
	if (plotSpec.x) {
		layout.xaxis.title = plotSpec.x.label;
	}
	if (plotSpec.y) {
		layout.yaxis.title = plotSpec.y.label;
	}

	// create data object
	let data = [];

	for (var i = 0; i < plotSpec.data.length; i++) {
		let dataSpec = plotSpec.data[i];
		let columns = dataSpec.df;
		let dataStatic = dataSpec.data_static;
		let dataToIterate = dataSpec.data_to_iterate;

		// increment legend group (even if we're not going to use it)
		g_autoLegendGroupId++;

		// loop over columns in data frame
		for (var j = 1; j < columns.length; j++) {
			let column = columns[j];
			let dataItem = {
				x: columns[0].values,
				y: columns[j].values,
				name: column.name,
			}; // fix(soon): initialize dataItem with copy of dataSpec so no need to copy individual attributes
			if (dataSpec.name) { 
				dataItem.name = dataSpec.name;
			}

			// dataStatic is a dictionary of values to set across the entire df, each trace will have the same static value
			if (dataStatic) {
				for (const [key, value] of Object.entries(dataStatic)) {
					dataItem[key] = value;
				}
			}

			// dataToIterate is a dictionary of values that differ by column for the df
			if (dataToIterate) {
				for (const [key, value] of Object.entries(dataToIterate)) {
					if (Array.isArray(value)) {
						if (value.length >= j) {
							dataItem[key] = value[j-1];	
						} else {
							console.log(`ERROR; dataToIterate doesn't contain enough entries for ${key}`);	
						}
					} else {
						console.log(`ERROR; dataToIterate didn't contain an array for ${key}`);
					}
				}
			}

			// TODO - it's probably worth cleaning up the 4 identical checks for markers, lines, widths, and opacities
			if (plotSpec.markers) {
				// for charts where multiple dfs are passed through, check to see if the attribute exists for the current df
				if (plotSpec.data.length > 1) {
					if (plotSpec.markers.length > i) {
						if (plotSpec.markers[i] && plotSpec.markers[i].length >= j) {
							dataItem.marker = plotSpec.markers[i][j-1];
						}
					}
				} else {
					dataItem.marker = plotSpec.markers[j-1];
				}
			}

			if (plotSpec.lines) {
				// for charts where multiple dfs are passed through, check to see if the attribute exists for the current df
				if (plotSpec.data.length > 1) {
					if (plotSpec.lines.length > i) {
						if (plotSpec.lines[i] && plotSpec.lines[i].length >= j) {
							dataItem.line = plotSpec.lines[i][j-1];
						}
					}
				} else {
					dataItem.line = plotSpec.lines[j-1];
				}
			}

			if (plotSpec.widths) {
				// for charts where multiple dfs are passed through, check to see if the attribute exists for the current df
				if (plotSpec.data.length > 1) {
					if (plotSpec.widths.length > i) {
						if (plotSpec.widths[i] && plotSpec.widths[i].length >= j) {
							dataItem.width = plotSpec.widths[i][j-1];
						}
					}
				} else {
					dataItem.width = plotSpec.widths[j-1];
				}
			}

			if (plotSpec.opacities) {
				// for charts where multiple dfs are passed through, check to see if the attribute exists for the current df
				if (plotSpec.data.length > 1) {
					if (plotSpec.opacities.length > i) {
						if (plotSpec.opacities[i] && plotSpec.opacities[i].length >= j) {
							dataItem.opacity = plotSpec.opacities[i][j-1];
						}
					}
				} else {
					dataItem.opacity = plotSpec.opacities[j-1];
				}
			}

			if (dataSpec.type === 'pie') {
				dataItem['labels'] = columns[0].values;
				dataItem['values'] = columns[1].values;
				dataItem['type'] = 'pie';
				
				if (dataSpec.hole) {
					dataItem['hole'] = dataSpec.hole;
				}

				delete dataItem['x'];
				delete dataItem['y'];
				delete layout['xaxis'];
				delete layout['yaxis'];

				data.push(dataItem);
				break;
			} else if (dataSpec.type === 'ohlc') {
				// data for OHLC: loop over the columns to set the elements: open, high, low, close
				// TODO assert(plotSpec.data.length == 1)
				// TODO assert(columns.length == 4)
				delete dataItem['y'];
				for (j = 1; j < columns.length; j++) {
					dataItem[columns[j].name] = columns[j].values // dataItem[close] = df[close], etc
				};
				// use index (i.e. column[0] name if no spec name specified
				dataItem.name = plotSpec.name || columns[0].name;
				dataItem.type = 'ohlc';
				data.push(dataItem);
				break;
			} 

			// if error bars, add them
			if (dataSpec.errorBars) {
				let errorInfo = {
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
			
			// get formatting from dataSpec if not already provided by dataStatic or dataToIterate
			if (!dataItem.orientation && dataSpec.orientation) {
				dataItem.orientation = dataSpec.orientation;
			}
			if (!dataItem.fillcolor && dataSpec.fillcolor) {
				dataItem.fillcolor = dataSpec.fillcolor;
			}
			if (!dataItem.type && dataSpec.type !== 'line') {
				dataItem.type = dataSpec.type;
			}
			
			// handle continuous error bars
			if (dataSpec.type === 'continuousErrorBars') {
				if (!dataItem.legendgroup) {
					dataItem.legendgroup = 'lg' + g_autoLegendGroupId;
				}
				if (j == 2) {
					let means = columns[1].values;
					let devs = columns[2].values;
					let upper = [];
					let lower = [];
					for (var k = 0; k < dataItem.x.length; k++) {
						upper.push(means[k] + devs[k]);
						lower.push(means[k] - devs[k]);
					}
					dataItem.y = upper;
					dataItem.fill = 'tonexty';
					dataItem.line = {color: 'transparent'};
					dataItem.showlegend = false;
					dataItem.type = 'scatter';

					// make a copy for the lower bound
					let newDataItem = {};
					Object.keys(dataItem).forEach(function(key) {
						 newDataItem[key] = dataItem[key];
					}); 
					newDataItem.fill = null;
					newDataItem.y = lower;
					data.push(newDataItem);
					
				// handle mean line of continuous error bars
				} else {
					dataItem.type = 'scatter';
					dataItem.mode = 'lines';
				}
			}
			
			// handle second y axis
			if (dataSpec.y2) {
				dataItem.yaxis = 'y2';
				if (layout.yaxis2) {
					// if someone uses the y2label attribute, it should take precednece over the layout.yaxais2 title
					// if (!layout.yaxis2.title && plotSpec.y2 && plotSpec.y2.label) {
					if (plotSpec.y2 && plotSpec.y2.label) {
						layout.yaxis2.title = plotSpec.y2.label;
					}
					if (!layout.yaxis2.overlaying) {
						layout.yaxis2.overlaying = 'y';
					}
					if (!layout.yaxis2.side) {
						layout.yaxis2.side = 'right';
					}
				} else {
					layout.yaxis2 = {
						overlaying: 'y',
						side: 'right'
					};

					if (plotSpec.y2 && plotSpec.y2.label) {
						layout.yaxis2.title = plotSpec.y2.label;
					}
				}
			}
			
			// handle horizontal bar chart: swap x and y
			if (dataItem.orientation === 'h') {
				let x = dataItem.x;
				dataItem.x = dataItem.y;
				dataItem.y = x;
			}
			
			// handle histograms
			if (dataSpec.type === 'histogram') {
				dataItem = JSON.parse(JSON.stringify(dataSpec)); // make copy; assumes just simple data
				delete dataItem['df'];
				dataItem.x = columns[j].values;
				dataItem.name = dataSpec.name || columns[j].name; // use column name if no spec name specified
				if (plotSpec.markers) {
					dataItem.marker = plotSpec.markers[j-1];
				}
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
			
			// provide a default mode for stacked bar charts
			if (dataItem.type === 'stackedBar') {
				dataItem.type = 'bar';
				layout.barmode = 'stack';
			}

			// provide a default mode for overlay bar charts
			if (dataItem.type === 'overlayBar') {
				dataItem.type = 'bar';
				layout.barmode = 'overlay';
			}
			
			// provide a default mode for scatter plots
			if (dataItem.type === 'scatter' && !dataItem.mode && dataSpec.type !== 'continuousErrorBars') {
				dataItem.mode = 'markers';
			}

			// provide a default mode for line plots
			if (dataSpec.type === 'line' && !dataItem.mode) {
				dataItem.mode = 'lines';
			}
			//console.log(dataItem);
			data.push(dataItem);
		}
	}	

	// handle timestamps
	if (plotSpec.typeX === 'timestamp') {
		for (var i = 0; i < data.length; i++) {
			let x = data[i].x;
			let newX = [];
			let len = x.length;
			for (var j = 0; j < len; j++) {
				newX[j] = Date.parse(x[j]);
			}
			layout.xaxis.type = 'date';
			data[i].x = newX;
		}
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
	Plotly.newPlot(plotDiv, data, layout, {displayModeBar: false}); //staticPlot: staticPlot, 
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

	// append data variables: colorscale, reversescale, showscale (i.e. colorbar side scale)
	if (plotSpec.colorscale) {
		data[0]['colorscale'] = plotSpec.colorscale;
	}
	if (plotSpec.reversescale) {
		data[0]['reversescale'] = plotSpec.reversescale;
	}
	//if (plotSpec.showscale !== undefined) {
	if (plotSpec.showscale) {
		data[0]['showscale'] = plotSpec.showscale;
	}

	// create layout object
	var layout = { 
		xaxis: {}, 
		yaxis: {}
	};
	if (plotSpec.labelX) {
		layout.xaxis.title = plotSpec.labelX;
	}
	if (plotSpec.labelY) {
		layout.yaxis.title = plotSpec.labelY;
	}
	if (plotSpec.margin) {
		layout.margin = plotSpec.margin;
	}
	if (plotSpec.title) {
		layout.title = plotSpec.title;
	}
	
	// determine whether to include interactive elements
	var staticPlot = true;
	if (plotSpec.staticPlot !== undefined) {
		staticPlot = plotSpec.staticPlot;
	}

	// create the plot
	Plotly.newPlot(plotDiv, data, layout, {staticPlot: staticPlot});
}


function generateSankeyPlot(plotDiv, plotSpec) {


	var dataSpec = plotSpec.data[0];
	var columns = dataSpec.df;
	var nodeLabels = plotSpec.nodeLabels;
	var linkLabels = plotSpec.linkLabels;

	var data = {
		type: "sankey",
		orientation: dataSpec.orientation,
		node: {},

		link: {
			source: columns[1].values,
			target: columns[2].values,
			value: columns[3].values,
			label: linkLabels,
		}
	};

	// node labels are required. Add such if none provided
	if (nodeLabels ===  undefined){
		nodeLabels = [];
		for (var i = 0; i<data.link.value.length; i++){
			nodeLabels.push(i.toString());
		}
	}
	data.node.label = nodeLabels;


	var layout ={};
	if (plotSpec.layout !== undefined) {
		layout = plotSpec.layout;
	}
	if (plotSpec.title !== undefined){
		layout.title = plotSpec.title;
	}

	// determine whether to include interactive elements
	var staticPlot = false;
	if (plotSpec.staticPlot !== undefined) {
		staticPlot = plotSpec.staticPlot;
	}

	// create the plot
	Plotly.newPlot(plotDiv, [data], layout, {staticPlot: staticPlot});
}

function generateBoxPlot(plotDiv, plotSpec) {

	var dataSpec = plotSpec.data[0];
	var columns = dataSpec.df.slice(1);
	var names = plotSpec.names;
	var markers = plotSpec.markers;
	var boxpoints = plotSpec.boxpoints;
	var groups = dataSpec.groups;

	var data = [];
	for (var i = 0; i < columns.length; i++){
		trace = {
			type: "box", 
			y: columns[i].values,
			name: columns[i].name,
		};

		// Change trace.y to trace.x to switch to horizontal orientation
		if (dataSpec.orientation == 'h'){
			trace.x = trace.y;
			delete trace.y;
		}
		// Set box markers
		if (markers != null){
			trace.marker = markers[i];
		}
		// Set boxpoints
		if (boxpoints != null){
			trace.boxpoints = boxpoints[i];
		}
		// Set groups for vertical orientation
		if (groups != null && trace.x == null){
			trace.x = groups;
		}
		// Set groups for horizontal orientation
		else if (groups != null && trace.y == null){
			trace.y = groups;
		}
		
		data.push(trace);
	}

	var layout ={};
	if (plotSpec.layout !== undefined) {
		layout = plotSpec.layout;
	}
	if (plotSpec.title !== undefined){
		layout.title = plotSpec.title;
	}

	var staticPlot = false;
	if (plotSpec.staticPlot !== undefined) {
		staticPlot = plotSpec.staticPlot;
	}

	// create the plot
	Plotly.newPlot(plotDiv, data, layout, {staticPlot: staticPlot});
}


function createMetric(context, label, data) {
	return context.metric(function(start, stop, step, callback) {
				callback(null, data);
			}, label);
}


/* from https://stackoverflow.com/questions/27012854/change-iso-date-string-to-date-object-javascript */
function parseISOString(s) {
	var b = s.split(/\D+/);
	return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
}


function generateCubismPlot(plotDiv, plotSpec) {

	var size = plotSpec.plots[0].data.length;  // assume all plots have same number of data items for now

	var context = cubism.context()
		.serverDelay(Date.now() - parseISOString(plotSpec.startTimestamp) - plotSpec.timeStep * 1000.0 * size)
		.clientDelay(0)
		.step(plotSpec.timeStep * 1000.0)  // convert seconds to milliseconds
		.size(size)  // number of data items
		.stop();  // don't attempt to do live updates

	d3.select('#' + plotDiv.id).call(function(div) {

		div.attr('style', 'width:' + size + 'px;position:relative');  // needed to show cursor value in correct location

		div.append('div')
			.attr('class', 'axis')
			.call(context.axis().orient('top').ticks(plotSpec.tickCount).tickFormat(d3.time.format(plotSpec.timestampFormat)));

		for (var i = 0; i < plotSpec.plots.length; i++) {
			var plotItem = plotSpec.plots[i];
			var metric = createMetric(context, plotItem.label, plotItem.data);
			div.append('div')
				.datum(metric)
				.attr('class', 'horizon')
				.call(context.horizon()
					.height(plotItem.height)
					.extent([plotItem.min, plotItem.max])
				);
		}

		div.append('div')
			.attr('class', 'rule')
			.call(context.rule());

	});

	context.on("focus", function(i) {
		d3.selectAll(".value").style("right", i == null ? null : context.size() - i + "px");
	});
}
