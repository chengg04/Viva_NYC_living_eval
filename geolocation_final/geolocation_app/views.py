
# coding: utf-8

# In[1]:

from django.shortcuts import render

# Create your views here.
#GoogleResult in models.py is the object we will use to
#communicate between the view and the html template
#We need this because that's the only way to pass associated
#data from python to a template

#No need to run makemigrations and migrate (no harm though) if you
#don't intend saving the data to a database

from geolocation_app.models import GoogleResult
from geolocation_app.models import GoogleResult_time
from geolocation_app.models import GoogleResult_steps
import re


def index(request,trans_type='DRIVING',type='cafe',area='New York',category='Restaurants'):
    #Check if we're coming for the first time or through the
    #index page
    try:
        if request.GET['type']:
            type=request.GET['type']
    except:
        pass
    print(type)
    

    #Check if we're coming for the first time or through the
    #index page
    try:
        if request.GET['trans_type']:
            trans_type=request.GET['trans_type']
    except:
        pass
    print(trans_type)
    
    try:
        if request.GET['area']:
            area=request.GET['area']
    except:
        pass
    print(area)
    
    try:
        if request.GET['category']:
            category=request.GET['category']
    except:
        pass
    print(category)

    import urllib.request as ur
    import json
    from bs4 import BeautifulSoup
    context = dict()
    #You need to get an auth key from google
    #https://console.developers.google.com/flows/enableapi?apiid=places_backend&keyType=SERVER_SIDE&reusekey=true
    #When registering with Google, leave the
    #"Accept requests from these server addresses" field blank
    
    #Once you have the key, enable the various apps you want to use
    #Google places, google maps javascript and google geolocations are useful
    #here

    #THIS KEY HAS LIMITED USE. GET YOUR OWN KEY!!!
    AUTH_KEY = "AIzaSyCPE34R7tmpZ_F08FWeDNBy27I9iQfhnqk"
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
    address="times square new york"
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
    radius =500
    #search nearby
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
    context['type']=type


    context['result_time'] = result_time

    #Send the type as well so that we can display it on the html page
    #(This could be formatted better!)
    
    context['trans_type'] = trans_type
    print(result_time)
    context['address']=address
    
    #cost
    URLs = {"New York":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=New+York%2C+NY", 
        "Brooklyn":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=Brooklyn%2C+NY", 
        "Bronx":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=Bronx%2C+NY", 
        "Queens":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=Queens%2C+NY"}
    url = URLs[area]
    url_response = ur.urlopen(url,timeout=5)
    soup = BeautifulSoup(url_response)
    soup.prettify()
    table = soup.find("table", { "class" : "data_wide_table" })
    header = {'User-Agent': 'Mozilla/5.0'} 
    rows = table.find_all('tr')
    #print ("Cost of living in "+ area + ":")
    output = False
    result_dict=dict()
    result_list2=list()
    for row in rows:
        cells = []
        current_section = ''
        section_tag = row.find('th',class_='highlighted_th prices')
        if section_tag and output:
            break
        
        if section_tag:
            current_section = section_tag.get_text()
        
        if category == 'Restaurants' and current_section=='Restaurants':
            output = True
            #print (category)
            result_dict['cat']=category
            continue    
        if category == 'Markets' and current_section == 'Markets':
            output = True
            #print (category)
            result_dict['cat']=category
            continue   
        if category == 'Transportation' and current_section == 'Transportation':
            output = True
            #print (category)
            result_dict['cat']=category
            continue  
        if category == 'Utilities (Monthly)' and current_section == 'Utilities (Monthly)':
            output = True
            #print (category)
            result_dict['cat']=category
            continue  
        if category == 'Clothing And Shoes' and current_section == 'Clothing And Shoes':
            output = True
            #print (category)
            result_dict['cat']=category
            continue 
        if category == 'Rent Per Month' and current_section == 'Rent Per Month':
            output = True
            #print (category)
            result_dict['cat']=category
            continue
        if category == 'Buy Apartment Price' and current_section == 'Buy Apartment Price':
            output = True
            #print (category)
            result_dict['cat']=category
            continue 

        if output:
            cells = row.find_all('td')
            str2 = cells[0].get_text()[:-1] + ':' + cells[1].get_text()[:-2]+' $'
            #print (str2)
            result_list2.append(str2)
    result_dict['cost']=result_list2

    if category == 'Comparison': 
        result_dict['cat']=category
        URLs = {"Brooklyn":"http://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&country2=United+States&city1=New+York%2C+NY&city2=Brooklyn%2C+NY", 
            "Bronx":"http://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&country2=United+States&city1=New+York%2C+NY&city2=Bronx%2C+NY", 
            "Queens":"http://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&country2=United+States&city1=New+York%2C+NY&city2=Queens%2C+NY"}

        if area == "New York":
            #print ("no comparison")
            result_list2=["no comparison"]
            result_dict['cost']=result_list2
        else: 
            #print ("Cost of Living in", area , "compared with New York:")
            result_list2.append("Cost of Living in "+ area+" compared with Manhattan: ")
            url = URLs[area]
            url_response=ur.urlopen(url,timeout=5)
            header = {'User-Agent': 'Mozilla/5.0'} 
            soup = BeautifulSoup(url_response)
            soup.prettify()

            table = soup.find("table", {"class": "table_indices_diff"})
            rows = table.find_all(["th", "td"])
        
            for row in rows:
                #print (row.text)
                result_list2.append(row.text.replace("New York","Manhattan"))
        result_dict['cost']=result_list2
        
    #pass vars
    if area== "New York":
        context['area']="Manhattan"
    else:
        context['area']=area
    context['cat']=result_dict['cat']
    context['result_list3']=result_list2
    print(result_list2)
    
    
    #crime
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
        if regex.findall(item['name'])!=[]:
            precinct=regex.findall(item['name'])
            break
    i = int(precinct[0])
    PCTnumber=[1,5,6,7,9,10,13,14,17,18,19,20,22,23,24,25,26,28,30,32,33,34,40,41,42,43,44,45,46,47,48,49,50,52,60,61,62,63,66,67,68,69,70,71,72,73,75,76,77,78,79,81,83,84,88,90,94,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,120,121,122,123]
    p=PCTnumber.index(i)+1


    import numpy as np
    data = np.genfromtxt('D:\programming_files\github\Viva_NYC_living_eval\dataforPCT.csv',delimiter=',')
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
    

        data = np.genfromtxt('D:\programming_files\github\pythonproject\dataforPCT.csv',delimiter=',')
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
        datapie = np.genfromtxt('D:\programming_files\github\Viva_NYC_living_eval\piechart.csv',delimiter=',')
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

