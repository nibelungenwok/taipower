# taipower
this project using python Scrapy framework to get power generation data from taipower webpage
https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html

I use crontab to periodically run this crawler script on a raspberry pi 4,
This generates 
<ul>
<li>a csv file: contains power generation data,</li>
<li>a screenshot png file: a screenshot of above taipower webpage,</li>
<li>a stdout/err log file: for debugging,</li>
</ul>
