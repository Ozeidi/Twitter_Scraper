import json 
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
#import pyautogui

#from tkinter import filedialog, Tk
#import tkinter.messagebox as tm
import os
from urllib.request import urlopen
import pandas as pd
import numpy as np
import requests
import csv
import datetime

import login
## Database 
import psycopg2
import pymysql
import subprocess

Auth =None
with open('Auth.json') as json_file:
    Auth = json.load(json_file)

# pyinstaller --onefile --icon=app.ico scrapejobs.py
#Chrome Paths on Heroku
#GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
#CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
if os.environ['APP_SETTINGS'] == 'PROD':
    from Settings.prod import *
elif os.environ['APP_SETTINGS'] == "DEV":
    from Settings.dev import * 
#pyautogui.FAILSAFE= False
class LinkedInSpider:

    MAX_APPLICATIONS =3000

    def __init__(self,username,password, language, position, location): #, resumeloctn):
        #heroku Datbase
        #self.conn = conn = psycopg2.connect("host=ec2-174-129-254-217.compute-1.amazonaws.com dbname=daj9b3ubq7bp3s user=kcuqkrlonouqek port=5432 password=69e1ad83317e3b92bb5145bd01c9abff9191fadb0b2e2d8a461ba83b32c3be14")
        #local Database for testing
        #psycopg2.connect("host=localhost dbname=linkedin user=ozeidi password=WadiFida.net1")
        #####################
        #Cloud SQL on Google
        # Initiate Proxy Connection Required by Google for Database Connection
        start_proxy = './cloud_sql_proxy -instances=pi-counter-263618:us-central1:pi-counter=tcp:3355 \
              -credential_file=pi-counter-263618-f7ca42a074df.json &'
        subprocess.call([start_proxy], shell=True)
        # Start the connection through the proxy tunnle
        self.conn = pymysql.connect(host='127.0.0.1',
                             port = 3355,
                             user=Auth["google"]["user"],
                             password=Auth["google"]["pass"],
                             db='Workforce')
        self.cur = self.conn.cursor()

        self.language = language
        self.options = self.browser_options()
        self.browser = webdriver.Chrome(chrome_options=self.options, executable_path =CHROMEDRIVER_PATH)
        self.start_linkedin(username,password)


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

        # Herok Options
        #options.add_argument('--disable-gpu')
        #options.binary_location = GOOGLE_CHROME_PATH 
        return options

    def start_linkedin(self,username,password):
        print("\nLogging in.....\n \nPlease wait :) \n ")
        self.browser.get("https://www.linkedin.com/")
        try:
            user_field = self.browser.find_element_by_name("session_key")
            pw_field = self.browser.find_element_by_name("session_password")
            login_button = self.browser.find_element_by_class_name("sign-in-form__submit-btn") 
            user_field.send_keys(username)
            user_field.send_keys(Keys.TAB)
            time.sleep(1)
            pw_field.send_keys(password)
            time.sleep(1)
            login_button.click()
        except TimeoutException:
            print("TimeoutException! Username/password field or login button not found.")

    def wait_for_login(self):
        if language == "en":
             title = "Sign In to LinkedIn"
        elif language == "es":
             title = "Inicia sesion"
        elif language == "pt":
             title = "Entrar no LinkedIn"

        time.sleep(1)

        while True:
            if self.browser.title != title:
                print("\nStarting LinkedIn bot\n")
                break
            else:
                time.sleep(1)
                print("\nPlease Login to your LinkedIn account\n")

    def fill_data(self):
        self.browser.set_window_size(0, 0)
        self.browser.set_window_position(2000, 2000)
        os.system("reset")

        self.position = position
        self.location = "&location=" + location


    def start_scraping(self):
        self.fill_data()
        self.applications_loop()

    def applications_loop(self):

        count_application = 1
        count_job = 0
        jobs_per_page = 0

        os.system("reset")

        print("\nLooking for jobs.. Please wait..\n")

        self.browser.set_window_position(0, 0)
        self.browser.maximize_window()
        self.browser, _ = self.next_jobs_page(jobs_per_page)
        
        print("\nLooking for jobs.. Please wait..\n")

        # self.browser.find_element_by_class_name(
        #     "jobs-search-dropdown__trigger-icon"
        #     ).click()
        
        # self.browser.find_element_by_class_name(
        #     "jobs-search-dropdown__option"
        #     ).click()

        while count_application < self.MAX_APPLICATIONS:
            # sleep to make sure everything loads, add random to make us look human.
            time.sleep(random.uniform(3.5, 6.9))
            # this to load all the jobs in the reactive pan
            #self.browser.execute_script('document.getElementById("ember218").scrollIntoView();')
            
            page = BeautifulSoup(self.browser.page_source, 'lxml')

            jobs = self.get_job_links(page)
            print( "########### NUMBER OF JOBS: {}".format(len(jobs)))
            if not jobs:
                print("Jobs not found")
                break

            for job in jobs:
                temp = {}

                count_job += 1
                job_page = self.get_job_page(job)

                #position_number = str(count_job + jobs_per_page)
                position_number = str(count_application)
                print("\nPosition {0}:\n {1} \n".format(position_number,self.browser.title)) # {string_easy} \n")
                print(job,'Omar \n')

                now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                temp ['timestamp'] = str(now)
                temp ['url'] = ('https://www.linkedin.com'+job)




                """
                click button see more
                """
                try :
                    self.browser.find_element_by_xpath('//*[@id="ember42"]'
                        #'//button[@aria-controls="job-details"]'
                        ).click()
                    # self.browser.find_element_by_class_name(
                    #     'view-more-icon'
                    #     ).click()
                    #self.load_page(sleep=1)
                except:
                    try:
                        self.browser.find_element_by_xpath('//*[@id="ember40"]').click()
                    except:

                        print('******* Job not valid *******\n')



                """
                Get data
                """     

                # position
                try:
                    temp['position'] = self.browser.find_element_by_xpath(
                        '//h1[@class="jobs-top-card__job-title t-24"]'
                        ).text.strip()
                except:
                    temp['position'] = None
                
                # company
                try:
                    temp['company'] = self.browser.find_element_by_xpath(
                        '//span[contains(text(),"Company Name")]/following::a'
                        ).text.strip()
                except:
                    temp['company'] = None        
                
                # location
                try:
                    temp['location'] = self.browser.find_element_by_xpath(
                        '//span[contains(text(),"Company Location")]/following::span'
                        ).text.strip()
                except:
                    temp['location'] = None  
                
                # post date
                try:
                    temp['post_date'] = self.browser.find_element_by_xpath(
                        '//span[contains(text(),"Posted Date")]/following::span'
                        ).text.strip()
                except:
                    temp['post_date'] = None  
                
                # no. of applicants
                try:
                    temp['no_applicants']  = self.browser.find_element_by_xpath(
                        '//span[contains(text(),"Number of applicants")]/following::span'
                        ).text.strip()
                except:
                    temp['no_applicants'] = None  

                # job details
                try:
                    temp['job_description'] = self.browser.find_element_by_xpath(
                        '//div[@id="job-details"]'
                        ).text.strip().replace('\n', ', ')
                except:
                    temp['job_description'] = None  
                
                # seniority level
                try:
                    temp['seniority'] = self.browser.find_element_by_xpath(
                        '//h3[contains(text(),"Seniority Level")]/following::*'
                        ).text.strip()
                except:
                    temp['seniority'] = None  
                
                # Industry
                try:
                    temp['industry'] = self.browser.find_element_by_xpath(
                        '//h3[contains(text(),"Industry")]/following::*'
                        ).text.strip()
                except:
                    temp['industry'] = None  
                
                # Employment Type
                try:
                    temp['employment_type'] = self.browser.find_element_by_xpath(
                        '//h3[contains(text(),"Employment Type")]/following::*'
                        ).text.strip()
                except:
                    temp['employment_type'] = None  
                
                #Job Functions
                try:
                    temp['functions'] = self.browser.find_element_by_xpath(
                        '//h3[contains(text(),"Job Functions")]/following::*'
                        ).text.strip()
                except:
                    temp['functions'] = None  

                # company description
                try:
                    temp['company_description'] = self.browser.find_element_by_id(
                        'company-description-text'
                        ).text.strip()
                except:
                    temp['company_description'] = None




                """
                Write to file
                """

                data = temp
                with open('output.csv', 'a', newline='') as f:
                    try:

                        writer = csv.writer(f)
                        if count_application ==1:
                            writer.writerow(data.keys())
                        writer.writerow(data.values())
                        print('Job added to output.csv')
                        

                    except:
                        print('*** Ooopss, NOT able to write job to output, sorry :(')

                    try:
                        self.do_insert(data)
                    except Exception as e:
                        print('*** Ooopss, NOT able to write to Database:(')
                        print(str(e))
                


                """
                Count application and set sleep time
                """
                count_application = count_application + 1

                if count_application % 200 == 0:
                    sleepTime = random.randint(1,3)#(590, 900)
                    print('\n\n****************************************\n\n')
                    print('Time for a nap - see you in ', sleepTime/60, ' min')
                    print('\n\n****************************************\n\n')
                    time.sleep (sleepTime)
                # that &start= parameter in the url http request refers to the page, where each page has 25 job postings
                #  25 means page 1, 50 page and so on
                if count_job == len(jobs):
                    jobs_per_page = jobs_per_page + 10
                    count_job = 0
                    print('\n\n****************************************\n\n')
                    print('Going to next jobs page, YEAAAHHH!!')
                    print('\n\n****************************************\n\n')
                    #self.avoid_lock()
                    self.browser, jobs_per_page = self.next_jobs_page(jobs_per_page)



        #self.finish_apply()

    def get_job_links(self, page):
        links = []
        for link in page.find_all('a'):
            url = link.get('href')
            if url:
                if '/jobs/view' in url:
                    links.append(url)
        return set(links)

    def get_job_page(self, job):
        root = 'linkedin.com'
        if root not in job:
            job = 'https://www.linkedin.com'+job
        self.browser.get(job)
        self.job_page = self.load_page(sleep=0.5)
        return self.job_page

    def got_easy_apply(self, page):
        button = page.find("button", class_="jobs-s-apply__button js-apply-button")
        return len(str(button)) > 4

    def get_easy_apply_button(self):
        button_class = "jobs-s-apply--top-card jobs-s-apply--fadein inline-flex mr2 jobs-s-apply ember-view"
        button = self.job_page.find("div", class_=button_class)
        return button

    def easy_apply_xpath(self):
        button = self.get_easy_apply_button()
        button_inner_html = str(button)
        list_of_words = button_inner_html.split()
        next_word = [word for word in list_of_words if "ember" in word and "id" in word]
        ember = next_word[0][:-1]
        xpath = '//*[@'+ember+']/button'
        return xpath

    def click_button(self, xpath):
        triggerDropDown = self.browser.find_element_by_xpath(xpath)
        time.sleep(0.5)
        triggerDropDown.click()
        time.sleep(1)

    def load_page(self, sleep=1):
        #MOVE TO PANE
        # pyautogui.moveTo(500, 500, duration=1.0)
        # x, _ = pyautogui.position()
        # pyautogui.moveTo(x+200, None, duration=1.0)
        # pyautogui.moveTo(x, None, duration=0.5)
        scroll_page = 4000
        while scroll_page < 4000:
            self.browser.execute_script("window.scrollTo(0,"+str(scroll_page)+" );")
            scroll_page += 200
            time.sleep(0.5)

        if sleep != 1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep * 3)

        page = BeautifulSoup(self.browser.page_source, "lxml")
        return page

    def avoid_lock(self):
        x, _ = pyautogui.position()
        pyautogui.moveTo(x+200, None, duration=1.0)
        pyautogui.moveTo(x, None, duration=0.5)
        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(0.5)
        pyautogui.press('esc')

    def next_jobs_page(self, jobs_per_page):
        self.browser.get(
            #"https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=" +86400
            # Jobs posted in the Last 7 Days
            "https://www.linkedin.com/jobs/search/?f_TPR=r604800&keywords=" +
            #Jobs Posted in the last 24 hours 
            #"https://www.linkedin.com/jobs/search/?f_TPR=r86400&keywords=" +
            self.position + self.location + "&start="+str(jobs_per_page)+"&sortBy=DD")
        #self.avoid_lock()
        self.load_page()
        return (self.browser, jobs_per_page)

    def finish_apply(self):
        self.browser.close()

    def do_insert(self, rec: dict):
        cols = rec.keys()
        cols_str = ','.join(cols)
        vals = [ rec[k] for k in cols ]
        vals_str = ','.join( ['%s' for i in range(len(vals))] ) 
        sql_str = """INSERT INTO Workforce ({}) VALUES ({})""".format(cols_str, vals_str)
        self.cur.execute(sql_str, vals)
        self.conn.commit()
if __name__ == '__main__':

    # set use of gui (T/F)
    useGUI = False

    # no gui
    if useGUI == False:

        username = Auth["linkedin"]["user"]#'consulting@intelligentdc.co' #'omazei@hotmail.com'#
        password = Auth["linkedin"]["pass"] #'WadiFida.net'#
        language = 'EN'
        position = ''
        location = 'Oman'

    # print input
    print("\nThese is your input:")

    print  ("\nUsername:  "+ username,
        "\nPassword:  "+ password,
        "\nLanguage:  "+ language,
        "\nPosition:  "+ position,
        "\nLocation:  "+ location)
    
    print("\nLet's scrape some jobs!\n")
    
    # start bot
    spider = LinkedInSpider(username,password, language, position, location) #, resumeloctn)
    spider.start_scraping()
