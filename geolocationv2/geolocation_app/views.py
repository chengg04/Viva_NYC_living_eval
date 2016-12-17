from django.shortcuts import render

# Create your views here.
#GoogleResult in models.py is the object we will use to
#communicate between the view and the html template
#We need this because that's the only way to pass associated
#data from python to a template

#No need to run makemigrations and migrate (no harm though) if you
#don't intend saving the data to a database


from geolocation_app.models import GoogleResult_time
from geolocation_app.models import GoogleResult_steps
import re


def index(request,trans_type='DRIVING'):
    #Check if we're coming for the first time or through the
    #index page
    
    

    #Check if we're coming for the first time or through the
    #index page
    try:
        if request.GET['trans_type']:
            trans_type=request.GET['trans_type']
    except:
        pass
    print(trans_type)

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
    AUTH_KEY = "AIzaSyAyU7DP39sDYFxP3gRmC0z1N2VMUx60ErM"
    #Default lat and lon
    lat =40.758889
    lon = -73.985278
    lat2 = 40.8075355
    lon2 = -73.9625727
    origin = "times square new york"
    destination = "columbia university new york"
    #If the user has entered an address in the html page
    #Get the latitude and longitude from there
    #Otherwise, just use the default
    address='times square new york'
    try:
        address = request.GET['address']
        address2 = request.GET['address2']
        #replace spaces with a + for the url
        address = '+'.join(address.split())
        address2 = '+'.join(address2.split())
        print(address)
        print(address2)
        #Construct the url to send to google
        url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
               '?query=%s'
               '&key=%s') % (address,AUTH_KEY)
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
        
        url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
               '?query=%s'
               '&key=%s') % (address2,AUTH_KEY)
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
        lat2 = geometry['location']['lat']
        lon2 = geometry['location']['lng']
        print(lat2,lon2)

    except:
        pass
    context['lat'] = lat
    context['lon'] = lon
    location = str(lat) + "," + str(lon)
    context['lat2'] = lat2
    context['lon2'] = lon2
    destination = str(lat2) + "," + str(lon2)

    #search police precinct

        #Construct the places url to send to google. Google will return a JSON object
    #directions
    url = ('https://maps.googleapis.com/maps/api/directions/json'
           '?origin=%s'
           '&destination=%s'
           '&mode=%s'
           '&key=%s') % (location, destination, trans_type.lower(), AUTH_KEY)
    response = ur.urlopen(url)
    jsonRaw = response.read().decode('utf-8')
    jsonData = json.loads(jsonRaw)
    k=jsonData['routes'][0]['legs'][0]
    result_time = GoogleResult_time(r_startlat = k['start_location']['lat'],r_startlon = k['start_location']['lng'],r_destlat = k['end_location']['lat'],r_destlon = k['end_location']['lng'],origin=k['start_address'],destination2=k['end_address'])
    result_time.r_time=k['duration']['text']

    steps=list()
    pattern = "<[^>]*>"
    regex = re.compile(pattern)
    for result in k['steps']:
        steps_detail=GoogleResult_steps(step=regex.sub("",result['html_instructions']))
        steps_detail.time=result['duration']['text']
        steps.append(steps_detail)
    context['steps']=steps
    


    context['result_time'] = result_time

    #Send the type as well so that we can display it on the html page
    #(This could be formatted better!)
    
    context['trans_type'] = trans_type
    print(result_time)
    context['address']=address
    m="police precinct near "+address
    police_precinct_query = '+'.join(m.split())
    url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
               '?query=%s'
               '&key=%s') % (police_precinct_query, AUTH_KEY)
    response = ur.urlopen(url)
    jsonRaw = response.read().decode('utf-8')
    jsonData = json.loads(jsonRaw)
    results = jsonData['results']
    pattern="(\d+)"
    regex = re.compile(pattern)
    precinct=[]
    for item in results:
        k=regex.findall(item['name'])
        if k!=[]:
            precinct=k
            break
    i = int(precinct[0])
    PCTnumber=[1,5,6,7,9,10,13,14,17,18,19,20,22,23,24,25,26,28,30,32,33,34,40,41,42,43,44,45,46,47,48,49,50,52,60,61,62,63,66,67,68,69,70,71,72,73,75,76,77,78,79,81,83,84,88,90,94,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,120,121,122,123]
    p=PCTnumber.index(i)+1

    import numpy as np
    data = np.genfromtxt('D:/programming_files/github/pythonproject/geolocationv2siyi/dataforPCT.csv',delimiter=',')
    average=np.average(data[1:,16])
    std=np.std(data[1:,16])
    if data[p,16]<average-std:
        msg='This precinct is relatively safe'
    else:
        if data[p,16]>average-std:
            msg='This precinct is relatively unsafe'
        else:
            msg='This precinct is in average safety level'
    context['msg'] = msg
    context['precinct'] = i
    #render the page
    return render(request,'index.html',context)



#crime plot
def simple(request):
        import urllib.request as ur
        import json
        import re
        import django
        import numpy as np
        try:
            address = request.GET['address']
            i=request.GET['precinct']
        except:
            pass
    

        data = np.genfromtxt('D:/programming_files/github/pythonproject/geolocationv2siyi/dataforPCT.csv',delimiter=',')
        PCTnumber=[1,5,6,7,9,10,13,14,17,18,19,20,22,23,24,25,26,28,30,32,33,34,40,41,42,43,44,45,46,47,48,49,50,52,60,61,62,63,66,67,68,69,70,71,72,73,75,76,77,78,79,81,83,84,88,90,94,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,120,121,122,123]
        i = int(i)
        
        p=PCTnumber.index(i)+1
        PCT=data[p,:16]
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
    
        fig=Figure(figsize=(16,5))
        ax=fig.add_subplot(1,2,1)
        ax.plot(PCT)
        ax.set_xlabel('Year start from 2000')
        ax.set_ylabel('Number of crime')
        ax.set_title('Trend of crime')


        ax2=fig.add_subplot(1,2,2)
        datapie = np.genfromtxt('D:/programming_files/github/pythonproject/geolocationv2siyi/dataforPCT.csv',delimiter=',')
        labels = 'MURDER & NON NEGL. MANSLAUGHTER', 'RAPE', 'ROBBERY', 'FELONY ASSAULT','BURGLARY','GRAND LARCENY','GRAND LARCENY OF MOTOR VEHICLE '
        start=7*p-6
        end=7*p+1
        sizes = datapie[start:end,17]
        colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue','blue','orange','black']
        explode = (0.1, 0, 0, 0,0, 0, 0)  # explode 1st slice

#     try:
        ax2.pie(sizes, explode=explode, labels=labels, colors=colors,autopct='%1.1f%%', shadow=True, startangle=10)
#         break
#     except ValueError:
#         print "Oops!  That was no valid number.  Try again..."

        ax2.axis('equal')
        ax2.set_title('Component of crime')
        canvas=FigureCanvas(fig)
        response=django.http.HttpResponse(content_type='image/png')
        canvas.print_png(response)
        return response
