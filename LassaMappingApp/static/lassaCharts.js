
function lassaBarChart(host){
	if (host == "human"){
		var myPlot = document.getElementById('myDiv');
		let AbTime = [];
		let AbProp = [];
		for (var i in propAb){
			AbTime.push(propAb[i].Ab_year);
			AbProp.push(propAb[i].propAbPos);
		};
		var dataGroupByDiagMethod = {};
		for (var i in propAb){
			var DiagMethod = propAb[i].DiagnosticMethod;
			if (!dataGroupByDiagMethod[DiagMethod]){
				dataGroupByDiagMethod[DiagMethod] = [];
			};
			dataGroupByDiagMethod[DiagMethod].push(propAb[i]);
		};
		data2 = [];
		for (var key in dataGroupByDiagMethod){
			Ab_year = [];
			propAbPos = [];
			for (var i in dataGroupByDiagMethod[key]){
				Ab_year.push(dataGroupByDiagMethod[key][i].Ab_year);
				propAbPos.push(dataGroupByDiagMethod[key][i].propAbPos);
			};
			var trace = {
				x: Ab_year,
				y: propAbPos,
				name: 'Serology: '.concat(key),
				type: 'bar',
				barmode: 'group',
			};
			data2.push(trace);
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
				bgcolor: 'rgba(0,0,0,0)',
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
			name: 'Serology',
			marker: {color: '#f0ad4e'}
		}];
		let modeBarButtons = [["toImage", "lasso2d"]];
		Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false});
		myPlot.on('plotly_doubleclick', function(){
			Plotly.newPlot('myDiv', data2, layout, {modeBarButtons, responsive:true, displaylogo:false});
		});
                myPlot.on('plotly_click', function(){
                        Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false});
                });
		myPlot.on('plotly_legendclick',function() { return false; });
	};
	if (host == "rodent"){
		var myPlot = document.getElementById('myDiv');
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
				bgcolor: 'rgba(0,0,0,0)',
				x: 0.45,
				xanchor: 'center',
				y: 1,
				"orientation": "h"
			}
		};
		var AbMethod = {};
		var VirusMethod = {};
                for (var i in propAb){
                        var AbDiagMethod = propAb[i].AbDiagnosticMethod;
                        if (!AbMethod[AbDiagMethod]){
                                AbMethod[AbDiagMethod] = [];
                        };
                        AbMethod[AbDiagMethod].push(propAb[i]);
                };
                for (var i in propAg){
                        var VirusDiagMethod = propAg[i].VirusDiagnosticMethod;
                        if (!VirusMethod[VirusDiagMethod]){
                                VirusMethod[VirusDiagMethod] = [];
                        };
                        VirusMethod[VirusDiagMethod].push(propAg[i]);
                };
                data2 = [];
                for (var key in AbMethod){
                        Ab_year = [];
                        propAbPos = [];
                        for (var i in AbMethod[key]){
                                Ab_year.push(AbMethod[key][i].Ab_year);
                                propAbPos.push(AbMethod[key][i].propAbPos);
                        };
			var t1name = 'Serology: '.concat(key);
                        var trace1 = {
                                x: Ab_year,
                                y: propAbPos,
                                name: t1name,
                                type: 'bar',
                                barmode: 'group',
                        };
                        data2.push(trace1);
                };
                for (var key in VirusMethod){
                        Ag_year = [];
                        propAgPos = [];
                        for (var i in VirusMethod[key]){
                                Ag_year.push(VirusMethod[key][i].Ag_year);
                                propAgPos.push(VirusMethod[key][i].propAgPos);
                        };
                        var t2name = 'Virus detection: '.concat(key);
                        var trace2 = {
                                x: Ag_year,
                                y: propAgPos,
                                name: t2name,
                                type: 'bar',
                                barmode: 'group',
                        };
                        data2.push(trace2);
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
			name: 'Virus detection',
			type: 'bar',
			barmode: 'group',
			marker: {color: '#7f7fff'}
		};
		var trace2 = {
			x: AgTime,
			y: AgProp,
			name: 'Serology',
			type: 'bar',
			barmode: 'group',
			marker: {color: '#f0ad4e'}
		};
		var data = [trace1, trace2];
		let modeBarButtons = [["toImage", "lasso2d"]];
		Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false});
                myPlot.on('plotly_doubleclick', function(){
                        Plotly.newPlot('myDiv', data2, layout, {modeBarButtons, responsive:true, displaylogo:false});
                });
		myPlot.on('plotly_legendclick',function() { return false; });
	};
	
	if (host=="sequence rodent"){
		var finalTitle = "Viral Sequences: Rodents";
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
			yaxis:{title: {text: 'Number of Sequences'}},
			showlegend: true,
			legend: {
	 			bgcolor: 'rgba(0,0,0,0)',
				x: 0.45,
				xanchor: 'center',
				y: 1,
				"orientation": "h"
			}
		};
		let modeBarButtons = [["toImage", "lasso2d"]];
		Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false});
		var myPlot = document.getElementById('myDiv');
		myPlot.on('plotly_legendclick',function() { return false; });
	};
        if (host=="sequence human"){
                var finalTitle = "Viral Sequences: Humans";
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
                        yaxis:{title: {text: 'Number of Sequences'}},
                        showlegend: true,
                        legend: {
				bgcolor: 'rgba(0,0,0,0)',
                                x: 0.45,
                                xanchor: 'center',
                                y: 1,
                                "orientation": "h"
                        }
                };
                let modeBarButtons = [["toImage", "lasso2d"]];
                Plotly.newPlot('myDiv', data, layout, {modeBarButtons, responsive:true, displaylogo:false});
		var myPlot = document.getElementById('myDiv');
		myPlot.on('plotly_legendclick',function() { return false; });
        };
};

