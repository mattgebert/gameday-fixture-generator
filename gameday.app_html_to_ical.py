# %%##########################################################
############# Import Dependencies for the script #############
##############################################################
import urllib.request as urlreq
from bs4 import BeautifulSoup
import pandas as pd
from icalendar import Calendar, Event, vText
import datetime, pytz

# %%##########################################################
########### Choose Website Link for Season Fixture ###########
##############################################################

# Waverley City FC Mens 5ths
url =   r"https://websites.mygameday.app/team_info.cgi?c=0-8912-204159-622721-26842503&a=SFIX"

# Waverley City FC Mens 4ths
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-204159-622720-26842517&a=SFIX"

# Waverley City FC Mens 3rds
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-204159-622717-26842487&a=SFIX"

# Waverley City FC Mens 2nds
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-204159-622719-26842516&a=SFIX"

# Waverley City FC Mens 1sts
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-204159-622709-26942525&a=SFIX"

# Waverley City FC Womens 1sts
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-204159-623783-26842909&a=SFIX"

# Donvale Firsts
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-126274-622717-24415450&a=SFIX"

# Donvale Seconds
# url = r"https://websites.mygameday.app/team_info.cgi?c=0-8912-126274-622721-24415662&a=SFIX"

# %%##########################################################
################# Get URL Webpage Text Format ################
##############################################################
# obj = urlreq.urlopen(url)
obj = urlreq.urlopen(url)
fixture = obj.read()

# %%##########################################################
############## Scrape Season Events using Soup ###############
##############################################################
# https://stackoverflow.com/questions/44584569/how-to-get-particular-tag-data-from-url-in-python-from-urllib2

soup = BeautifulSoup(fixture, features="html.parser")
seasonFixDiv = soup.find("div", {"id": "seasonFix"})

# %%##########################################################
############## Format and process season events ##############
##############################################################

#Team Name
banner = seasonFixDiv.find('h2', {"class": "blockHeading"})
teamname = banner.text.split(":")[1].split("(")[0].strip()

#Table of Events
tabulka = seasonFixDiv.find("table", {"class": "tableClass"})
rows = tabulka.findAll('tr')

#Get Data Headers
headers = [hd.text.strip() for hd in rows[0].findAll("th")]
#Get Data Columns
records = []
for row in rows[1:]:
    cols = row.findAll('td')
    data = [coli.text.strip() for coli in cols] #strip space unicode characters \xa0.
    if len(data) == len(headers):
        print(data)
        records.append(data)
        

# %%##########################################################
############## Get google maps venue location  ###############
##############################################################
#Note this step can take a while as it needs to load each location webpage...

parse_location = True #Set to false if not working...
location_string = "VENUE/COURT"
div_class = "venue-map-info"
base_url = "https://websites.mygameday.app//"
map_links = []
if parse_location:
    for row in rows[1:]:
        cols = row.findAll('td')
        for i in range(len(cols)):
            if headers[i] == location_string:
                mapurl = cols[i].find("a", href=True)["href"] #extract relative url from <a> link
                # Open map url
                map = urlreq.urlopen(base_url + mapurl)
                maphtml = map.read()
                mapsoup = BeautifulSoup(maphtml,features="html.parser")
                mapinfo = mapsoup.find("div",{"class":"venue-map-info"})
                googlemaplink = mapinfo.find("a", href=True)["href"]
                print(googlemaplink)
                map_links.append(googlemaplink)
    

# %%##########################################################
############ Cleanup empty whitespaces from data #############
##############################################################
for i in range(len(headers),0,-1):
    j = i-1 #convert to index
    if headers[j] == "":
        headers.pop(j)
        for r in records:
            r.pop(j)


# %%##########################################################
################ Convert to Pandas to View ###################
##############################################################
pd_records = pd.DataFrame(records, columns=headers)
maps_col = "MAPLINK"
pd_records[maps_col] = map_links
print(pd_records)


# %%##########################################################
########### Convert fields to meaningful values ##############
##############################################################

#manually set field values
date_col = "DATE" #index for date data
time_col = "TIME" #index for time data
rnd_col = "RND" #index for round number
opp_col = "OPPOSITION" #index for opposition name
year_init = "20" #makesup the first two missing year characters.
pydatetime = "DATETIME"
loc_col = "VENUE/COURT"

tz = pytz.timezone("Australia/Sydney") #Will account for default "Daylight savings"
#convert time data to useful format
times = []
for i in range(pd_records.shape[0]):
    date = pd_records[date_col][i].split("(")[0].split("/")[::-1]
    date[0] = year_init + date[0]
    date = [int(j) for j in date]
    time = [int(j) for j in pd_records[time_col][i].split(":")]
    params = date + time
    dt = datetime.datetime(*params)
    match_time = tz.localize(dt)
    print(match_time)
    times.append(match_time)
pd_records[pydatetime] = times
    
# %%##########################################################
############### Generate ical calendar file ##################
##############################################################

# https://icalendar.readthedocs.io/en/latest/usage.html#example
# https://support.google.com/calendar/answer/37118?hl=en#Create-or-edit-an-icalendar-file&zippy=%2Ccreate-or-edit-an-icalendar-file

#Create Fixture Calendar
fcal = Calendar()
fcal.add('prodid', '-//My calendar product//mxm.dk//')
fcal.add('version', '2.0')

match_duration = 2 #hours

for i in range(pd_records.shape[0]):
    round = pd_records[rnd_col][i]
    round_time = pd_records[pydatetime][i]
    opposition = pd_records[opp_col][i]
    loc = pd_records[loc_col][i]
    loc_url = pd_records[maps_col][i]
    
    #Generate event
    e = Event()
    e.add("summary", "VCFA:Rnd " + str(round) + " - " + opposition)
    # Timing
    e.add("dtstart", round_time)
    endtime = round_time + datetime.timedelta(hours=match_duration)
    e.add("dtend", endtime)
    e.add("dtstamp", datetime.datetime.now(tz=tz))
    # Location & Maps URL
    e.add('location', vText(loc), {"ALTREP": vText(loc_url)})
    e.add('description', vText(loc_url + "\n" + teamname + " vs " + opposition + " at " + loc))
    
    #Add event to calendar
    fcal.add_component(e)
    
    # break #for testing..

# %%
import os
cwd = os.getcwd()
write_loc = cwd #unless specified
print(write_loc)

filename = str(datetime.datetime.now().year) + "-" + teamname + "-fixture.ical"
f = open(os.path.join(write_loc, filename), 'wb')
f.write(fcal.to_ical())
f.close()

# %%
