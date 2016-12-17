from django.shortcuts import render

# Create your views here.
#GoogleResult in models.py is the object we will use to
#communicate between the view and the html template
#We need this because that's the only way to pass associated
#data from python to a template

#No need to run makemigrations and migrate (no harm though) if you
#don't intend saving the data to a database

from geolocation_app.models import GoogleResult
from geolocation_app.models import GoogleResult_cost

def index(request,type='cafe',county_type='new york',cat_type='Resaurant'):
    #Check if we're coming for the first time or through the
    #index page
	try:
		if request.GET['type']:
			type=request.GET['type']
	except:
		pass
	print(type)


	##
	current_section=''
	try:
		if request.GET['county_type']:
			county_type=request.GET['county_type']
	except:
		pass
	print(county_type)
	
	try:
		if request.GET['current_section']:
			current_section=request.GET['current_section']
	except:
		pass
	print(current_section)
    
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
	location =str(lat) + "," + str(lon)
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
	
	from bs4 import BeautifulSoup
	URLs = {"new york":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=New+York%2C+NY", 
        "brooklyn":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=Brooklyn%2C+NY", 
        "bronx":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=Bronx%2C+NY", 
        "queens":"http://www.numbeo.com/cost-of-living/city_result.jsp?country=United+States&city=Queens%2C+NY"}
	county_type=county_type
	url = URLs['%s'%(county_type)]
	cat_type=cat_type
	
	url_response=ur.urlopen(url)
	soup = BeautifulSoup(url_response)
	soup.prettify()
	#print(soup)
	for table in soup.find_all('table', class_='data_wide_table'):

		rows = table.find_all('tr')
	header = {'User-Agent': 'Mozilla/5.0'}
	for row in rows:
		cells = []
		results =[]
		result_list2=list()
		result_list3=list()
		section_tag = row.find('th',class_='highlighted_th prices')
		output = False
		if section_tag and output:
			break

		if section_tag:
			current_section = section_tag.get_text()
		if current_section == 'Restaurants' and cat_type == 1:
			output = True
			result_list2.append(current_section)
			continue    
		if current_section == 'Markets' and cat_type == 2:
			output = True
			result_list2.append(current_section)
			continue   
		if current_section == 'Transportation' and cat_type == 3:
			output = True
			result_list2.append(current_section)
			continue  
		if current_section == 'Utilities (Monthly)' and cat_type == 4:
			output = True
			result_list2.append(current_section)
			continue  
		if current_section == 'Clothing And Shoes' and cat_type == 5:
			output = True
			result_list2.append(current_section)
			continue 
		if current_section == 'Rent Per Month' and cat_type == 6:
			output = True
			result_list2.append(current_section)
			continue
		if current_section == 'Buy Apartment Price' and cat_type == 7:
			output = True
			result_list2.append(current_section)
			continue 
		if output:
			cells = row.find_all('td')
			str_2 = cells[0].get_text() + '\t' + cells[1].get_text()
			result_list2.append(str_2)
		if current_section=='Comparison': #cat_type == 8:
			URLs = {"brooklyn":"http://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&country2=United+States&city1=New+York%2C+NY&city2=Brooklyn%2C+NY",
            "bronx":"http://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&country2=United+States&city1=New+York%2C+NY&city2=Bronx%2C+NY", 
            "queens":"http://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&country2=United+States&city1=New+York%2C+NY&city2=Queens%2C+NY"}

			if county_type == "new york":
				result_list2.append('no comparison')
			else: 
				comp=("Cost of Living in "+ county_type + " compare with New York:/n")     
				result_list2.append(comp)
				url = URLs[county_type]
				url_response=ur.urlopen(url,timeout=5)
				header = {'User-Agent': 'Mozilla/5.0'} 
				soup = BeautifulSoup(url_response)
				soup.prettify()

				for table in soup.find_all('table', class_='table_indices_diff'):
					rows = table.find_all(["th", "td"])
				for row in rows:
					comp2=result_list2+row+'/n'
					result_list2.append(comp2)
			result_list3=list()
			for result in result_list2:
				res_detail=GoogleResult_cost(result_text=result)
				result_list3.append(res_detail)
		context['result_list3']=result_list3	
		
		
    #Send the type as well so that we can display it on the html page
    #(This could be formatted better!)
	context['type'] = type
	print(result_list2)
    #render the page
	return render(request,'index.html',context)

