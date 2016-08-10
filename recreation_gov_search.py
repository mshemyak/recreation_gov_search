#!/usr/bin/env python
import argparse
import copy
import requests
import smtplib

import urllib
from urlparse import parse_qs
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Hardcoded list of campgrounds I'm willing to sleep at
PARKS = {
    '73984': 'PINNACLES'
}

# Sets the search location to Pinnacles
LOCATION_PAYLOAD = {
    'currentMaximumWindow': '12',
    'locationCriteria': 'PINNACLES CAMPGROUND',
    'interest': '',
    'locationPosition': 'NRSO:73984:-121.1761111:36.4663889::CA',
    'selectedLocationCriteria': '',
    'resetAllFilters':    'true',
    'filtersFormSubmitted': 'false',
    'glocIndex':    '0'
}

SECOND_PAYLOAD = {
    'resetAllFilters' :  'false',
    'filtersFormSubmitted' :  'true',
    'sortBy' :  'RELEVANCE',
    'category' :  'camping',
    'selectedState' :  '',
    'selectedActivity' :  '',
    'selectedAgency' :  '',
    'interest' :  'camping',
    'usingCampingForm' :  'true'
}

FINAL_PAYLOAD = {
    'resetAllFilters' :  'false',
    'filtersFormSubmitted' :  'true',
    'sortBy' :  'RELEVANCE',
    'category' :  'camping',
    'arrivalDate' :  'Fri Aug 19 2016', #gets overwritten by the command line params
    'departureDate' :  'Sat Aug 20 2016',
    'flexDates' :  '',
    'availability' :  'all',
    'selectedState' :  '',
    'selectedActivity' :  '',
    'lookingFor' :  '',
    'camping_common_218' :  '',
    'camping_common_3012' :  '',
    'camping_common_3013' :  '',
    'selectedAgency' :  '',
    'interest' :  'camping',
    'usingCampingForm' :  'false'
}

BASE_URL = "http://www.recreation.gov"
UNIF_SEARCH = "/unifSearch.do"
UNIF_RESULTS = "/unifSearchResults.do"

def findCampSites(args):
    payload = updateDates(args['start_date'], args['end_date'])
    content_raw = sendRequest(payload)
    html = BeautifulSoup(content_raw, 'html.parser')
    sites = getSiteList(html)
    return sites

def getNextDay(date):
    date_object = datetime.strptime(date, "%Y-%m-%d")
    next_day = date_object + timedelta(days=1)
    return datetime.strftime(next_day, "%Y-%m-%d")

def formatDate(date):
    date_object = datetime.strptime(date, "%Y-%m-%d")
    date_formatted = datetime.strftime(date_object, "%a %b %d %Y")
    return date_formatted

def updateDates(start, end):
    payload = copy.copy(FINAL_PAYLOAD)
    payload['arrivalDate'] = formatDate(start)
    payload['departureDate'] = formatDate(end)
    return payload

def getSiteList(html):
    sites = html.findAll('div', {"class": "check_avail_panel"})
    results = []
    for site in sites:
        if site.find('a', {'class': 'book_now'}):
            get_url = site.find('a', {'class': 'book_now'})['href']
            # Strip down to get query parameters
            get_query = get_url[get_url.find("?") + 1:] if get_url.find("?") >= 0 else get_url
            if get_query:
                get_params = parse_qs(get_query)
                siteId = get_params['parkId']
                if siteId and siteId[0] in PARKS:
                    results.append("%s, Booking Url: %s" % (PARKS[siteId[0]], BASE_URL + get_url))
    return results

def sendRequest(payload):
    with requests.Session() as s:
        
        s.get(BASE_URL + UNIF_RESULTS) # Sets session cookie
        s.post(BASE_URL + UNIF_RESULTS, LOCATION_PAYLOAD) # Sets location to specified spot
        s.post(BASE_URL + UNIF_RESULTS, SECOND_PAYLOAD) # Sets search to camping (selects the camping radio button)
        resp = s.post(BASE_URL + UNIF_RESULTS, payload) # Runs search on specified dates

        if (resp.status_code != 200):
            raise Exception("failedRequest","ERROR, %d code received from %s".format(resp.status_code, BASE_URL + SEARCH_PATH))
        else:
            return resp.text

def send_email(message):

    sender = 'youraddress@gmail.com'
    recipient = ["addr1@example.com", "addr2@gmail.com"]
    password = 'your_gmail_password'

    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        
        subject = "Campsites available!"
        headers = "\r\n".join(["from: " + sender,
                               "subject: " + subject,
                               "mime-version: 1.0",
                               "content-type: text/html"])
        content = headers + "\r\n\r\n" + message

        server.sendmail(sender, recipient, content)
        server.quit()
    except Exception:
        logging.exception('Failed to send succcess e-mail.')



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date", required=True, type=str, help="Start date [YYYY-MM-DD]")
    parser.add_argument("--end_date", type=str, help="End date [YYYY-MM-DD]")

    args = parser.parse_args()
    arg_dict = vars(args)
    if 'end_date' not in arg_dict or not arg_dict['end_date']:
        arg_dict['end_date'] = getNextDay(arg_dict['start_date'])

    sites = findCampSites(arg_dict)

    email_output = " "
    if sites:
        email_output = "sites available: \n"
        for site in sites:
            email_output = "\n" + email_output + site + \
                "&arrivalDate={}&departureDate={}" \
                .format(
                        urllib.quote_plus(formatDate(arg_dict['start_date'])),
                        urllib.quote_plus(formatDate(arg_dict['end_date'])))
    if email_output != " ":
        print email_output
        send_email(email_output)

