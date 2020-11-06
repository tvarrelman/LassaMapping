var mapOptions = {center: [9.531665, 4.460415], zoom:4};
var map = new L.map("map", mapOptions);
var layer = new L.TileLayer('//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
map.addLayer(layer);
var markers = L.markerClusterGroup();
//var SY = document.getElementById("StartYear");
//SY.options[0].selected = true;
//var EY = document.getElementById("EndYear");
//EY.options[EY.options.length - 1].selected = true;
var start_year_select = $('#StartYear'),
end_year_select = $('#EndYear');
//console.log(start_year_select.val());

function getUpdatedEndYear(start_val, host) {
      var send = {
              start_year: start_val,
              host: host
      };
      $.ajax({async:false, url:"/_get_end_year", data:send, dataType:"json",
              success: function(data){
                      end_year_select.empty();
                      for (var i in data){
                              //console.log(data);
                              end_year_select.append(
                                      $('<option>',{
                                              value: data[i].end_year,
                                              text: data[i].end_year},
                                      '</option>'))
                      }              
              }
      });
};

function GetFilteredPoints(startYear, endYear, host){
	var NewCoords = null;
	var send_years = {
		start_year: startYear,
		end_year: endYear,
		host: host
	};
	$.ajax({async:false, url:"/_filter_points", data:send_years, dataType:"json",
		success: function(data){
			result=data;
		}
	});
	return result;
};

function MapPoints(NewCoords, host, map){
	var map = map;
	markers.clearLayers();
	map.removeLayer(markers);
        for (var i in NewCoords){
                coordPair = NewCoords[i];
                if (host=="human"){
			var myIcon = L.icon({
        			iconUrl: '/static/images/baseline_person_black_18dp.png',
        			iconSize: [35,35]
			});
                        var Ablabel ="<b>Proportion arenavirus positive:</b> " + coordPair.PropAb;
                        var Citation = "<b>Citation:</b> " + coordPair.Citation;
                        if (coordPair.DOI == "NaN"){
                                DOI = "<b>DOI:</b> NaN";
                        } else {
                                var DOI = "<b>DOI:</b> <a href='https://doi.org/" + coordPair.DOI +"'>link</a>";
                        }
                        title = Ablabel + "<br> <br>" + Citation + "<br> <br>" + DOI ;
                }
                if (host == "rodent"){
                        var myIcon = L.icon({
				iconUrl: '/static/images/baseline_pest_control_rodent_black_18dp.png',
				iconSize: [35,35]
			});
			var Ablabel ="<b>Proportion arenavirus positive:</b> " + coordPair.PropAb;
                        var Aglabel="<b>Proportion Lassa virus positive:</b> " + coordPair.PropAg;
                        var Citation = "<b> Citation:</b> " + coordPair.Citation;
                        if (coordPair.DOI == "NaN"){
                                DOI = "<b>DOI:</b> NaN";
                        } else {
                                var DOI = "<b>DOI:</b> <a href='https://doi.org/" + coordPair.DOI +"'>link</a>";
                        }
                        title = Ablabel + "<br> <br>" + Aglabel + "<br> <br>" + Citation + "<br> <br>" + DOI
                }
                if (host=="sequence"){
                        var gbDef =  "<b>GenBank description:</b> " + coordPair.gbDefinition;
                        var ref = "<b>Reference:</b> " + coordPair.Reference;
                        if (coordPair.gbPubMedID == "NaN"){
                                PubMedID = "<b>PubMed:</b> NaN";
                        } else {
                                var PubMedID = "<b>PubMed:</b> <a href='https://pubmed.ncbi.nlm.nih.gov/" + coordPair.gbPubMedID +"'>link</a>";
                        }
                        title = gbDef + "<br> <br>" + ref + "<br> <br>" + PubMedID ;
                }
                var marker = L.marker(new L.LatLng(coordPair.Latitude, coordPair.Longitude, { title: title}));
                marker.bindPopup(title);
                marker.setIcon(myIcon);
                markers.addLayer(marker);
        }
	map.addLayer(markers);
};