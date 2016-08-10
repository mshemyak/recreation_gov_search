# Checking reservation.gov for campsite availability, and notifying via email.

Python script that checks campsite availability and if any sites are found for the specified dates, sends an email. It can be scheduled to run periodically to look for cancellations.  

I based this on https://github.com/bri-bri/yosemite-camping but edited because the code on github didn't work for me (looks like recreation.gov changed some things on their side), and then added email notifications via gmail, mostly copy/pasting code snippets I found online.

Keep in mind that this was my first time looking at Python, and I really have next to no experience with web stuff. Any comments or changes welcome. 

I run this on Windows 10 using the Windows Task Scheduler, but I believe it should work on OSX or Linux as well without any changes, you'll just schedule using cron 


To make it work you'll need to 
* put in your own gmail credentials (currently harcoded)
* email recepients
* provide --start_date and --end_date as command line parameters

It's currently hardcoded for Pinnacles NP, to check for other campsites, follow bri-bri's instructions to specify campsites and capture the payload for the POST request (pasted below). I used Wireshark on Windows (my first time doing this), worked like a charm.

## Searching for parks other than Yosemite

### Get LOCATION_PAYLOAD request data
* Use your preferred proxy or network analyzer to capture requests (Charles Proxy, Wireshark, etc)
* Visit recreation.gov in your browser
* Enter target park name - click the park in the prefilled Auto-suggest dropdown that appears
* Find logs for the POST request to www.recreation.gov/unifSearch.do
* Copy the REQUEST body params as JSON into the `LOCATION_PAYLOAD` dict in `campsites.py`
* (keep the search results page open and continue to next section)

### Whitelist campsites by id in PARKS dict
* From the list of campgrounds and attractions listed in the results for your park, choose the campgrounds you'd like to stay at
* For each campground you choose, copy the campground's link URL
* Grab the parkId URL param and add it as a key to the PARKS dict in `campsites.py`, the value should be a human readable campground name.


