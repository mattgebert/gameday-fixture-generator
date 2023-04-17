# gameday-fixture-generator

A script to scrape mygameday.app for fixture events, then write them into an ical formatted file compatible with Google, Apple etc.

## How to use:
1. Install python 3 (add to path if you don't have it)
2. Install depdencenies (see below)
3. Run the script with python (see below).


## Dependencies:
urllib, bs4, pandas, icalendar, datetime, pytz

Only pandas pandas, icalendar are non-standard.

You can install using `pip install pandas icalendar` from command prompt.

## Running the script:
### From the local folder
Open command prompt in the same folder as the `.py` file, and run the script adding an argument for your team's fixture URL, using quotations such as "https://websites.mygameday.app/team_info.cgi?c=...&a=SFIX".

`python gameday.app_html_to_ical.py "URL"`

### Modify
Otherwise modify the script to include a url parameter (examples in file) and run it in your own code editor.
