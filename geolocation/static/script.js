/**
 * Created by DalekSupreme on 11/20/15.
 */
window.onload = function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;
            showMap(lat, lon);
    });
    } else {
    // Print out a message to the user.
        document.write('Your browser does not support GeoLocation');
    }
}

function show_map(lat,lon) {
    var myLatLng = new google.maps.LatLng(lat, lon);
    var mapOptions = {
        zoom: 8,
        center: {lat: -25.363882, lng: 131.044922 }
    };
    var map = new google.maps.Map(document.getElementById('map'), mapOptions);
}