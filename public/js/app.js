var heatmap, map, pointArray;
var domain = window.location.hostname;
_.templateSettings.variable = "rc";

var init = function() {
  var mapOptions = {
    zoom: 2,
    center: new google.maps.LatLng(48.5616572, 18.6395052),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  } 
  
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  
  pointArray = new google.maps.MVCArray([]);
  
  heatmap = new google.maps.visualization.HeatmapLayer({
    data: pointArray,
  });

  heatmap.setMap(map);
 }

var updateTweets = function(data) {
  //console.log("updateTweets: ", data);
  var template = _.template($("script.template").html());
  $("#tweets").prepend($(template(data)).hide().fadeIn(2000));
}

google.maps.event.addDomListener(window, 'load', init);

$(document).ready(function() {
  var sse = new EventSource("http://" + domain + ":5000/new_tweets");

  sse.onmessage = function(event) {
    if(event.data) {
      //console.log(event);
      var json = $.parseJSON(event.data); 
      //console.log(json);
      if(json.coordinates) {
        pointArray.push(new google.maps.LatLng(json.coordinates[1], json.coordinates[0]));
        updateTweets(json);
      }
    }
  }
});
