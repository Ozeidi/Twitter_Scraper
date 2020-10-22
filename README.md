# Twitter Scraper

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)



## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Resources](#Resources)
- [License](#license)

## Background
This project is an attempt to fetch data from twitter without the need for Twitter's Official API or Developer Account.
For my use case Twitter API had several limitations including:
1. Can't retrieve tweets more than 7 days old.
2. There is a rate limit on how many requests could be posted per minute.

This code base should enable you to collect data from twitter without need for account nor for developer access.

## Install

1. Clone this repo to your machine.

```sh
$ git clone https://github.com/Ozeidi/Twitter_Scraper.git
```
2. OPTIONAL: Create vrtual environemnt to avoid messing your python main environment:
```sh
$ python3 -m venv myenv
$ myenv/Scripts/activate.bat
```
3. cd into the cloned directory and install the package requirments. this might take few minutes to complete.
```sh
$ pip install -r requirements.txt 
```



## Usage
```sh
from Twitter_Scrapper import *

if __name__ == "__main__":
    spider = TwitterSpider ("Omantel")
    spider.ScrapProfile()
    print("Profile Scrapped")  
    spider.Harvest("output\{0}_Tweets.json".format(spider.user)) 

```
Import the Twitter_Scrapper module in your project and pass to it the handel of the twitter user you are interested in. The module have 2 functions:
1. ### ScrapProfile():

	 Collect all the tweets on the user public profile. Once completed, results will be saved in the output folder with file name `User_Tweets.json`. in the above code results will be in `Omantel_Tweets.json`. Results will be in the follwoing format:

	 ```sh 
	 {
        "ID": "/PDO_OM/status/1230474791423021056",
        "tweet": "",
        "timestamp": "2020-02-20T12:50:26.000Z",
        "replies": "1 Reply. Reply",
        "retweet": "13 Retweets. Retweet",
        "likes": "58 Likes. Like"
    } 
	```

	 **Note: Recently twitter started limiting the number of tweets in the user profile where older tweets get archived**

2. ### Harvest(): 

	Collect replies to each tweet. Results will be in the following format:

	```sh
	[
		{
        "ID": "https://twitter.com/Omantel/status/1183683445928673280",
        "replies": []
		},
		{
        "ID": "https://twitter.com/Omantel/status/1183683445928673280",
        "replies": []}
	]
	```

##  Resources
- https://www.vicinitas.io/ :
    An excellent website that gives you thorough analysis of a twitter account, Hashtage and Followers.
## License

[MIT](LICENSE) © Omar Al Zeidi