from django.shortcuts import render

# Create your views here.
#GoogleResult in models.py is the object we will use to
#communicate between the view and the html template
#We need this because that's the only way to pass associated
#data from python to a template

#No need to run makemigrations and migrate (no harm though) if you
#don't intend saving the data to a database

from geolocation_app.models import GoogleResult

def index(request,type='cafe'):
    #Check if we're coming for the first time or through the
    #index page
    try:
        if request.GET['type']:
            type=request.GET['type']
    except:
        pass
    print(type)
    import urllib.request as ur
    import json
    context = dict()
    #You need to get an auth key from google
    #https://console.developers.google.com/flows/enableapi?apiid=places_backend&keyType=SERVER_SIDE&reusekey=true
    #When registering with Google, leave the
    #"Accept requests from these server addresses" field blank
    
    #Once you have the key, enable the various apps you want to use
    #Google places, google maps javascript and google geolocations are useful
    #here

    #THIS KEY HAS LIMITED USE. GET YOUR OWN KEY!!!
    AUTH_KEY = "AIzaSyAFVj8rmymh1HZOcAf0NUX9Bt1RVeuC4PI"
    #Default lat and lon
    lat =40.758889
    lon = -73.985278
    #If the user has entered an address in the html page
    #Get the latitude and longitude from there
    #Otherwise, just use the default

    try:
        address = request.GET['address']
        #replace spaces with a + for the url
        address = '+'.join(address.split())
        print(address)
        #Construct the url to send to google
        url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s') % (address)
        print(url)
        #Get the response from google and make it readable
        response = ur.urlopen(url).read().decode('utf-8')
        print(response)
        #Convert from json to a python dictionary
        #Need import json somewhere before this
        response = json.loads(response)
        #Navigate through the multi-level dictionary till you get
        #the latitude and longitude
        response = response['results'][0]
        geometry = response['geometry']
        print(geometry)
        lat = geometry['location']['lat']
        lon = geometry['location']['lng']
        print(lat,lon)
    except:
        pass
    context['lat'] = lat
    context['lon'] = lon
    location = str(lat) + "," + str(lon)
    radius =500
    type = type
    #Construct the places url to send to google. Google will return a JSON object
    url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&radius=%s'
           '&types=%s'
           '&sensor=false&key=%s') % (location, radius, type, AUTH_KEY)
    response = ur.urlopen(url)
    jsonRaw = response.read().decode('utf-8')
    #json.loads loads a json file and converts it into a Python dictionary
    #need to import json
    jsonData = json.loads(jsonRaw)
    #Examine the json file for keys. This file contains one key: 'results'
    #The key maps to a list of results. Each result in the list corresponds
    # to one place and the data for each place is another dictionary
    results = jsonData['results']
    results_list = list()
    #Extra
    for result in results:
        res_detail = GoogleResult(r_name = result['name'],r_address = result['vicinity'])
        res_detail.r_lat = result['geometry']['location']['lat']
        res_detail.r_lon = result['geometry']['location']['lng']
        results_list.append(res_detail)
    #Put the results_list into the context dictionary
    context['results_list'] = results_list
    #Send the type as well so that we can display it on the html page
    #(This could be formatted better!)
    context['type'] = type
    print(results_list)
    #render the page
    return render(request,'index.html',context)

