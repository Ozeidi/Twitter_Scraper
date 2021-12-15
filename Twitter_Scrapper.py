
import itertools
import json 
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

import os
from urllib.request import urlopen

import pandas as pd
import numpy as np
import requests
import csv
import datetime

from Settings.dev import *

from collections import Iterable
def flatten(lis):
     for item in lis:
         if isinstance(item, Iterable) and not isinstance(item, str):
             for x in flatten(item):
                 yield x
         else:        
             yield item
def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item
class TwitterSpider:
    """
    A scraper to harvest tweets from profile without
    the need for twitter API
    """
    MAX_TWITS = 50000
    def __init__(self, user):

        print (CHROMEDRIVER_PATH)
        self.options = self.browser_options()
        self.browser = webdriver.Chrome(chrome_options=self.options, executable_path =CHROMEDRIVER_PATH)
        self.user= user
        self.wait_duration = 4

    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("user-agent=Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393")
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        #options.add_argument('--disable-gpu')
        #options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        return options

    def ScrapProfile(self):
        self.browser.get("https://twitter.com/{0}".format(self.user))


        # Get scroll height.
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        tweets_full_list = []
        cnt=0
        while True:
            tweets=[]
            # Scroll down to the bottom.
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(self.wait_duration )
            page = BeautifulSoup(self.browser.page_source, 'lxml')
            articles = page.select('article[role*="article"]')
            
            for article in articles:
                cnt +=1
                try:
                    tweet ={}
                    tweet['ID'] = (article.select('a[href*="/status/"]')[0]["href"])
                    tweet['tweet'] = (article.text)
                    tweet['timestamp'] = (article.select('time')[0]["datetime"])
                    tweet['replies'] = int(re.search('[0-9]+',(article.select('div[data-testid*="reply"]')[0]["aria-label"])).group())
                    tweet['retweet'] = int(re.search('[0-9]+',(article.select('div[data-testid*="retweet"]')[0]["aria-label"])).group())
                    tweet['likes'] = int(re.search('[0-9]+',(article.select('div[data-testid*="like"]')[0]["aria-label"])).group())
                    print("{0} Tweet collected!".format(cnt))
                    tweets.append(tweet)
                except:
                    print("{0} Tweet not available!".format(cnt))
            
            tweets_full_list.extend(tweets)
            #self.WriteJSON("Tweets_agg.json", tweets)
            # Calculate new scroll height and compare with last scroll height.
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height
            
            # if cnt >5:
            #     break
        self.WriteJSON("output/{0}_Tweets.json".format(self.user),tweets_full_list ) #list(itertools.chain(*tweets_full_list))
        #print (tweets)

    def Harvest(self, file):
        replies_full_list =[]
        data= ""
        cnt=0
        with open(file, "r") as f:
            data = json.load(f)
            for tweet in data:
                id_ = tweet["ID"]
                if   tweet["replies"] != 0:
                    result = self.HarvestReplies(id_)
                    
                    print(f"Replies Collected for tweet Number {cnt}, ID: {id_} ")
                    #print(result)
                    replies_full_list.extend(result)
                cnt+=1
                # if cnt >4:
                #     break
        #print(replies_full_list)
        self.WriteJSON("output/{0}_Replies.json".format(self.user), replies_full_list)


    def HarvestReplies(self, id):
        self.browser.get(f"https://twitter.com/{id}")

        # Get scroll height.
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        tweets_full_list = []
        cnt=0
        while True:
            tweets=[]
            # Scroll down to the bottom.
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(self.wait_duration )
            page = BeautifulSoup(self.browser.page_source, 'lxml')
            articles = page.select('article[role*="article"]')
            
            for article in articles:
                cnt +=1
                try:
                    tweet ={}
                    tweet['Parent ID'] = id
                    tweet['ID'] = (article.select('a[href*="/status/"]')[0]["href"])
                    tweet['tweet'] = (article.text)
                    tweet['timestamp'] = (article.select('time')[0]["datetime"])
                    tweet['replies'] = int(re.search('[0-9]+',(article.select('div[data-testid*="reply"]')[0]["aria-label"])).group())
                    tweet['retweet'] = int(re.search('[0-9]+',(article.select('div[data-testid*="retweet"]')[0]["aria-label"])).group())
                    tweet['likes'] = int(re.search('[0-9]+',(article.select('div[data-testid*="like"]')[0]["aria-label"])).group())
                    #
                    tweets.append(tweet)
                except:
                    print("{0} Tweet not available!".format(cnt))
            print(f"{cnt} Replies collected!")
            tweets_full_list.extend(tweets)
            #self.WriteJSON("Tweets_agg.json", tweets)
            # Calculate new scroll height and compare with last scroll height.
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                try:
                    ele = spider.browser.find_element_by_xpath("//span[contains(text(),'Show more replies')]")
                    
                    ele.click()
                except:
                    try:
                        ele = spider.browser.find_element_by_xpath("//span[text()='Show']")
                        ele.click()
                    except:
                        break

            last_height = new_height
            
            # if cnt >5:
            #     break
        #self.WriteJSON("output/{0}_Tweets.json".format(self.user),tweets_full_list ) #list(itertools.chain(*tweets_full_list))
        return tweets_full_list

    def ScrollDown(self):
        """A method for scrolling the page."""

        # Get scroll height.
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        cnt = 0
        while True:

            # Scroll down to the bottom.
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(self.wait_duration -1 )

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height
            

    def WriteCSV(self, file, data):
        """
        Write to file
        """

        with open(file, 'a+', newline='') as f:
            try:

                writer = csv.writer(f)
                writer.writerow(data)
                print('Job added to output.csv')
                

            except:
                print('*** Ooopss, NOT able to write job to output, sorry :(')
    def WriteJSON(self,file, data):
        """
        Write to json filefile
        """
        #print(file)
        with open(file, "w+", newline='') as f:
            try:
                f.write(json.dumps(data, indent=4))
                #f.write(",")
                #json.dump(data, f) 
                print('Job added to file')           
            except:
                print('*** Ooopss, NOT able to write job to output, sorry :(')
