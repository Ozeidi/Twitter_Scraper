
import itertools
import json 
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
        self.wait_duration = 2

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

        # while ScrollPage < self.MAX_TWITS:
        #      # sleep to make sure everything loads, add random to make us look human.
        #     time.sleep(random.uniform(1, 1))
        #     ScrollPage +=5000
        #     self.browser.execute_script("window.scrollTo(0,"+str(ScrollPage)+" );")
        # this to load all the jobs in the reactive pan
        #self.browser.execute_script('document.getElementById("ember218").scrollIntoView();')
        # Get scroll height.
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        tweets_full_list = []
        cnt=0
        while True:
            tweets=[]
            # Scroll down to the bottom.
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(2)
            page = BeautifulSoup(self.browser.page_source, 'lxml')
            articles = page.select('article[role*="article"]')
            
            for article in articles:
                cnt +=1
                tweet ={}
                tweet['ID'] = (article.select('a[href*="/status/"]')[0]["href"])
                tweet['tweet'] = (article.text)
                tweet['timestamp'] = (article.select('time')[0]["datetime"])
                tweet['replies'] = (article.select('div[data-testid*="reply"]')[0]["aria-label"])
                tweet['retweet'] = (article.select('div[data-testid*="retweet"]')[0]["aria-label"])
                tweet['likes'] = (article.select('div[data-testid*="like"]')[0]["aria-label"])
                print("{0} Tweet collected!".format(cnt))
                tweets.append(tweet)
            
            tweets_full_list.extend(tweets)
            #self.WriteJSON("Tweets_agg.json", tweets)
            # Calculate new scroll height and compare with last scroll height.
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height
            
            # if cnt >3:
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
                if  "0 Replies" not in tweet["replies"]:
                    result = self.HarvestReplies(id_)
                    
                    print("{0}Replies Collected!".format(cnt))
                    #print(result)
                    replies_full_list.append(result)
                cnt+=1
                # if cnt >4:
                #     break
        #print(replies_full_list)
        self.WriteJSON("output/{0}_Replies.json".format(self.user), replies_full_list)

    def HarvestReplies(self, id):

        tweet = []
        tweet_timestamp = ""
        replies = []
        link = "https://twitter.com{0}".format(id)
        while True:
            self.browser.get(link)
            # Wait to load the page.
            time.sleep(self.wait_duration) 
            page = BeautifulSoup(self.browser.page_source, 'lxml')
            temp = [txt.get_text().strip() for txt in page.select('div[data-testid*="tweet"]')]
            print(temp)
            if len(temp)!=0:
                break
            else:
                print("Reached Rate limit!")
                self.browser.close()
                self.browser = self.browser = webdriver.Chrome(chrome_options=self.options, executable_path =CHROMEDRIVER_PATH)

        last_height = self.browser.execute_script("return document.body.scrollHeight")



        #Interactions
        # likes = [txt.get_text().strip() for txt in page.select('a[href*="/likes"]')]
        # retweet = [txt.get_text().strip() for txt in page.select('a[href*="/retweet"]')]
        # qoute = [txt.get_text().strip() for txt in page.select('a[href*="/with_comment"]')]
        #------
        #REPLIES
        while True:

            temp = [txt.get_text().strip() for txt in page.select('div[data-testid*="tweet"]')]
            replies.append([x for x in temp if x !="" and x != 'PDO | شركة تنمية نفط عمان@PDO_OM'])
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(self.wait_duration)
            page = BeautifulSoup(self.browser.page_source, 'lxml')
            # Calculate new scroll height and compare with last scroll height.
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height
        temp = list(uniq(replies))
        # data = {"ID":link,  "likes":likes, "retweet":retweet, "qoute": qoute, "replies" : temp }
        data = {"ID":link,  "replies" : temp }
        #print(data)
        return data

    def ScrollDown(self):
        """A method for scrolling the page."""

        # Get scroll height.
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        cnt = 0
        while True:

            # Scroll down to the bottom.
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(2)

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
