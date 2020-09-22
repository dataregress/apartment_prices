# this is my first real python work for my project 'House Prices: Advanced Regression Techniques -  Dubai Edition'
# this scrapper goes through https://www.xxxxxx.xx/ and scraps the property details and save them into CSV

# i've used selenium and beautifulsoup for this purpose. i hope it's not unethical to use both :D

# credits:
# thank you to Ömer Sakarya from towardsdatascience.com. his code in scrapping glassdoor gave me the idea link below
# https://towardsdatascience.com/selenium-tutorial-scraping-glassdoor-com-in-10-minutes-3d0915c6d905
# feel free to fork and let me know how i did it. there's always room for improvement


# importing whats needed
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from os import path
import urllib3
import random


# it begins here. call this function kick start the whole chain
# parameters: number of properties, (filename including .csv extension)
def start_scrapping_properties(num_of_properties, filename):
    # calling function to scrap properties. passing number of properties to be extracted and filename for csv.
    scrap_properties(num_of_properties, filename)


# function to start the scrapping process and save the csv file
# parameters: number of properties, (filename including .csv extension)
def scrap_properties(num_of_properties, filename):

    urls = get_properties_url(num_of_properties)

    # saving list of urls to csv. so we don't loose progress after collecting all the urls
    url_df = pd.DataFrame(urls)
    url_df.to_csv('urls.csv')

    # calling function to get property details for all the urls. passing list of urls and object selenium driver
    if path.exists('urls.csv'):
        url_df = pd.read_csv('urls.csv')

    df = get_property_details(url_df['0'])

    # calling function to save the extracted dataframe into csv file
    save_data_csv(df, filename)


# function to save dataframe to csv file
# parameters: dataframe, filename (including .csv extension)
def save_data_csv(data_frame, filename):

    # checking if the file exist. delete if it is already there
    if path.exists(filename):
        os.remove(filename)

    # saving to csv. please include .csv extension in filename
    data_frame.to_csv(filename, index=False)


# function to get property urls
# parameters: number of properties
# returns: list containing urls
def get_properties_url(num_of_properties):

    # initializing the web driver
    options = webdriver.ChromeOptions()

    # change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(
        executable_path="F:\\Projects\\Apartment Price Prediction\\selenium_driver\\chromedriver.exe",
        options=options)
    driver.set_window_size(1120, 1000)

    # base url to start from. you can change parameters by opening the below url in browser
    # and then modify the onscreen filters, and then copy-paste the updated url below
    url = 'https://www.xxxxxxxx.xx/en/search?c=1&l=1&ob=mr&page=1&t=1'

    driver.get(url)

    property_urls = []

    # looping until the number of property
    while len(property_urls) < num_of_properties:
        time.sleep(5)
        property_cards = driver.find_elements_by_class_name("card-list__item")

        for property_card in property_cards:
            time.sleep(1)

            # checking if there is an ad appearing in the middle of the property listing
            # the first element of a valid property is always an A tag. If not, it's an ad
            if property_card.get_attribute('innerHTML').find('<a') < 0 or property_card.get_attribute('innerHTML')\
                    .find('<div') == 0:
                continue

            url_soup = BeautifulSoup(property_card.get_attribute('innerHTML'), 'html.parser')

            if len(property_urls) >= num_of_properties:
                break

            # skipping sponsor posts
            sponsor_post = url_soup.find("div", {"class": "sponsored-post"})
            if sponsor_post is not None:
                continue

            # getting the list of all anchor tags for property details page
            property_url = url_soup.find('a', {'class': 'card--clickable'})

            # getting the HREF attribute for the property details anchor tag and appending to list
            if len(property_url.attrs) > 0:
                purl = property_url.attrs['href']
                property_urls.append(purl)

        try:

            # there are 25 properties per page.
            # checking if the number of properties required exceeds that number, then navigating to next page
            # it keeps going until the required number of properties are not retrieved
            if len(property_urls) < num_of_properties:
                driver.find_element_by_class_name('pagination__link--next').click()
        except NoSuchElementException:
            print("scraping terminated before reaching target number of properties. Needed {}, got {}."
                  .format(num_of_properties, len(property_urls)))

    return property_urls


# function to scrap property details page
# parameters: list containing all property details page
# returns: dataframe containing property data
def get_property_details(list_property_urls):

    print('URLs collected:', len(list_property_urls))

    # initializing list for property data
    properties = []

    counter = 1

    # looping through property urls
    for prop_url in list_property_urls:

        try:
            print('Getting details of property ', counter, 'of', len(list_property_urls))

            collected_successfully = False

            # setting up variables and objects
            http = urllib3.PoolManager()
            prop_url_parts = prop_url.split('-')
            prop_url_last_part = prop_url_parts[-1]
            property_id = prop_url_last_part.replace('.html', '')
            property_lat = ''
            property_lon = ''
            property_type = ''
            property_size = ''
            property_bedrooms = ''
            property_bathrooms = ''
            property_locality = ''
            property_completion = ''

            # checking if the property detail has been captured
            while not collected_successfully:

                # making http call to get html content
                html = http.request('GET', prop_url)

                # condition to handle a scenario where property is already sold out but is still listed with message
                # not available
                if 'property-gone__area' in html.data.decode('utf-8'):
                    collected_successfully = True
                    continue

                # sleeping for 5 second to not attract attention
                # sleep_time = random.randint(3, 10)
                time.sleep(3)

                # loading property details page html to beautifulsoup
                prop_soup = BeautifulSoup(html.data, 'html.parser')

                # getting property title
                property_title = prop_soup.find('h1', {'class': 'property-page__title'}).text

                # getting property price
                prop_price_div = prop_soup.find('div', {'class': 'property-price__price'})
                property_price = prop_price_div.text
                property_price = property_price.replace('AED\n', '').strip()
                property_price = property_price.replace(',', '')

                # getting locality of the property
                property_locality_div = prop_soup.find('div', {'class': 'property-location__detail-area'})
                property_locality_div = property_locality_div.find('div', {'class': 'text text--size3'})
                if property_locality_div is not None:
                    property_locality = property_locality_div.text

                # getting property latitude and longitude details
                pattern = r'{"lat":[-+]?[0-9]*\.?[0-9]*,"lon":[-+]?[0-9]*\.?[0-9]*}'
                property_lat_long = re.search(pattern, html.data.decode('utf-8'))

                if property_lat_long is not None:
                    property_location = property_lat_long[0]
                    property_location = property_location.replace('{"lat":', '')
                    property_location = property_location.replace('"lon":', ' ')
                    property_location = property_location.replace('}', '')
                    property_lat = property_location.split(', ')[0]
                    property_lon = property_location.split(', ')[1]

                # getting list property facts
                property_facts = prop_soup.find_all('div', {'class': 'property-facts__list'})

                if len(property_facts) > 0:
                    # looping list of property facts
                    for property_fact in property_facts:

                        if len(property_fact.contents[0].attrs) < 2:
                            fact_name = property_fact.contents[0].text.strip()
                            fact_value = property_fact.contents[1].text.strip()

                            if fact_name == 'Completion:':
                                property_completion = fact_value

                            if fact_name == 'Property type:':
                                property_type = fact_value

                            if fact_name == 'Property size:':
                                property_size = fact_value

                            if fact_name == 'Bedrooms:':
                                property_bedrooms = fact_value

                            if fact_name == 'Bathrooms:':
                                property_bathrooms = fact_value

                # getting property amenities and converting them to comma separated string
                prop_amen = ''
                property_amenities = prop_soup.find_all('div', {'class': 'property-amenities__list'})
                if len(property_amenities) > 0:
                    for property_amenity in property_amenities:
                        prop_amen += property_amenity.text.strip() + ', '

                # storing property detail into multidimensional array
                properties.append({'id': property_id,
                                   'title': property_title,
                                   'price': property_price,
                                   'location': property_locality,
                                   'latitude': property_lat,
                                   'longitude': property_lon,
                                   'type': property_type,
                                   'size': property_size,
                                   'no_of_bedrooms': property_bedrooms,
                                   'no_of_bathrooms': property_bathrooms,
                                   'completion_status': property_completion,
                                   'amenities': prop_amen})

                # marking property details collected successfully
                collected_successfully = True

                counter += 1
        except:
            continue

    # returning dataframe
    return pd.DataFrame(properties)
