from Twitter_Scrapper import *

if __name__ == "__main__":
    spider = TwitterSpider ("Shell")
    spider.ScrapProfile()
    print("Profile Scrapped")  
    spider.Harvest("output/{0}_Tweets.json".format(spider.user)) 

