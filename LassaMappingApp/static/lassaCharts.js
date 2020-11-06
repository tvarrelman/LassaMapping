
function lassaBarChart(host){
	if (host == "human"){
		let AbTime = [];
		let AbProp = [];
		for (var i in propAb){
			AbTime.push(propAb[i].Ab_year);
			AbProp.push(propAb[i].propAbPos);
		};
		var finalTitle = "Viral Infection: Humans"
		var layout = {
			title: finalTitle,
			font: {color:'#1a1a1a'},
			autosize: true,
			automargin: false,
			margin: {
				l: 55,
				r: 10,
				b: 50,
				t: 50,
				pad: 4
			},
			xaxis:{title: {text: 'Year'}},
			yaxis:{title: {text: 'Proportion of Individuals'}},
			showlegend: true,
			legend: {
				x: 0.45,
				xanchor: 'center',
				y: 1,
				"orientation": "h"
				}
		};
		var data = [{
			x: AbTime,
			y: AbProp,
			type: 'bar',
			name: 'Arenavirus positive',
			marker: {color: '#f0ad4e'}
		}];
		let modeBarButtons = [["toImage", "lasso2d"]];
		Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false});
	};
	if (host == "rodent"){
		var finalTitle = "Viral Infection: Rodents"
		var layout = { 
			title: finalTitle,
			font: {color:'#1a1a1a'},
			autosize: true,
			automargin: false,
			margin: {
				l: 55,
				r: 10,
				b: 50,
				t: 50,
				pad: 4
			},
			xaxis:{title: {text: 'Year'}},
			yaxis:{title: {text: 'Proportion of Individuals'}},
			legend: {
				x: 0.45,
				xanchor: 'center',
				y: 1,
				"orientation": "h"
			}
		};
		let AbTime = [];
		let AbProp = [];
		for (var i in propAb){
			AbTime.push(propAb[i].Ab_year);
			AbProp.push(propAb[i].propAbPos);
		};
		let AgTime = [];
		let AgProp = [];
		for (var j in propAg){
			AgTime.push(propAg[j].Ag_year);
			AgProp.push(propAg[j].propAgPos);
		};
		var trace1 = {
			x: AbTime,
			y: AbProp,
			name: 'Lassa virus positive',
			type: 'bar',
			barmode: 'group',
			marker: {color: '#f0ad4e'}
		};
		var trace2 = {
			x: AgTime,
			y: AgProp,
			name: 'Arenavirus positive',
			type: 'bar',
			barmode: 'group',
			marker: {color: '#7f7fff'}
		};
		var data = [trace1, trace2];
		let modeBarButtons = [["toImage", "lasso2d"]];
		Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false})
	};
	
	if (host=="sequence"){
		var finalTitle = "Viral Sequences";
		let seqYear = [];
		let seqCount = [];
		for (var i in seqData){
			seqYear.push(seqData[i].seq_year);
			seqCount.push(seqData[i].seq_count); 
		};
		var data = [{
			x: seqYear,
			y: seqCount,
			name: 'Numer of Sequences',
			type: 'bar',
			marker: {color: '#f0ad4e'}
		}];
		var layout = { 
			title: finalTitle,
			font: {color:'#1a1a1a'},
			autosize: true,
			automargin: false,
			margin: {
				l: 55,
				r: 10,
				b: 50,
				t: 50,
				pad: 4
			},
			xaxis:{title: {text: 'Year'}},
			yaxis:{title: {text: 'Count'}},
			showlegend: true,
			legend: {
				x: 0.45,
				xanchor: 'center',
				y: 1,
				"orientation": "h"
			}
		};
		let modeBarButtons = [["toImage", "lasso2d"]];
		Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false})
	};
};

