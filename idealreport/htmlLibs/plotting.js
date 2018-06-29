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
			} else if (dataSpec.type === 'box') {

				dataItem['type'] = 'box';
				if (dataItem.orientation === 'h') {
					dataItem.x = columns[1].values;
					dataItem.y = dataSpec.groups;
				} else {
					dataItem.y = columns[1].values;
					dataItem.x = dataSpec.groups;
				}

				dataItem.name = dataSpec.name || columns[j].name;
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

	// colorscale 
	if (plotSpec.colorscale) {
		data[0]['colorscale'] = plotSpec.colorscale;
	}
	
	// include colorbar side scale
	var showscale = true;
	if (plotSpec.showscale !== undefined) {
		data[0]['showscale'] = plotSpec.showscale;
	}

	// create layout object
	var layout = { 
		xaxis: {}, 
		yaxis: {}
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
