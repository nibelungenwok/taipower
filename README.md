# taipower
this project using python Scrapy framework to get power generation data from taipower webpage
https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html

I use crontab to periodically run this crawler script on a raspberry pi 4
This generates 
a csv file: contains power generation data
a screenshot png file: a screenshot of above taipower webpage
a stdout/err log file: for debugging
