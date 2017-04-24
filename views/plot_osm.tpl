<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.1/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.0.1/dist/leaflet.js"></script>

</head>
<body>

<div>
    <p>Plotting OSM ids {{ids}}</p>
    <p>{{message}}</p>
</div>

<div id="mapid" style="width: 600px; height: 400px;"></div>
    <script>

        var mymap = L.map('mapid').setView([51.505, -0.09], 10);
        L.tileLayer('https://api.mapbox.com/styles/v1/bblay/ciutzgyag01062hpbar2p3zga/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYmJsYXkiLCJhIjoiY2l1c2syMzY1MDAyMjJ5bzgzZ2FvODVreCJ9.2HNE3D06-w89AhEoh7NQrQ', {
            maxZoom: 10,
            attribution: 'attribution',
            id: 'bblay.Light'
        }).addTo(mymap);

        {{ markers }}
        {{ polys }}

    </script>
</div>

</body>
</html>
