import os
import scrapy

from time import sleep
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timezone
# By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
# create dir if it not exists 
from create_dir import mkdir_p 
# csv
import csv

basedir = os.path.dirname(os.path.realpath('__file__'))
class taipowercrawler(scrapy.Spider):
    name = "tai"
    allowed_domains = ["www.taipower.com.tw"]
    start_urls = ["https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html" ]


    def parse(self, response):
        STR_DATE_TIME = '%Y_%m_%dT%H_%M_%S'
        start_time = datetime.now(tz=timezone.utc)
        start_time_string = start_time.astimezone().strftime(STR_DATE_TIME ) 
        '''
        we take screenshot after the data is updated
        usually the time that data is updated is 10mins earlier than the 
        time we take screenshot
        '''
        screenshot_filename = start_time_string + 'screenshot'
        '''
        screenshot will be saved in a directory 
        called (relative path)screenshot_dir under current directory
        we need create the path if the directory doesn't exist
        if user input a path that we don't have permission to access, use '.'
        '''
        screenshot_dir = "screenshots"
        # create screenshot_dir if it doesn't exist
        #screenshot_dir = "screenshots"
        if not mkdir_p(screenshot_dir):
            screenshot_dir = "."

        screenshot_path_filename = os.path.join(screenshot_dir, screenshot_filename)
        self.logger.info(f"screenshot_path_filename:{screenshot_path_filename}")  

        chrome_driver_path = os.path.join('/usr/bin', 'chromedriver')

        """
         download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
         the version of the driver must match the version of chrome installed to work
         instantiate a chrome options object so you can set the size and headless preference
        """
        self.logger.info(f"setup chrome")  
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--window-size=1024X7373")
        chrome_options.add_argument("--window-size=1280x9216")
        self.logger.info(f"done setup chrome")  


        # comment out the following two lines to setup ProxyMesh service
        # make sure you add the IP of the machine running this script to you ProxyMesh account for IP authentication
        # IP:PORT or HOST:PORT you get this in your account once you pay for a plan

        # PROXY = "us-wa.proxymesh.com:31280"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)

        self.logger.debug(chrome_driver_path)
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)

        ''' original URL
        driver.get("https://www.taipower.com.tw/tc/page.aspx?mid=206&cid=406&cchk=b6134cc6-838c-4bb9-b77a-0b0094afd49d")
        '''
        # this url updates data in 10min interval, not every 10mins from 00min
        URL_IFRAME_TAIPOWER= "https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html"
        driver.get(URL_IFRAME_TAIPOWER) 

        # need to wait for 2nd part of the webpage and the data of power generation by each plants
        self.logger.info("wait for webpage to be rendered")
        timeout = 10
        xpath_nuclear_group_title_element = '/html/body/div[2]/div[4]/div/div/table/tbody/tr[1]'
        element_presence = ec.presence_of_element_located((By.XPATH, xpath_nuclear_group_title_element))
        nuclear_group_titel_element = WebDriverWait(driver, timeout).until(element_presence)
        self.logger.info("done wait for webpage to be rendered")
        

        self.logger.info(f"save screenshot {screenshot_path_filename}.png")  
        # take screeshot of the screen 
        driver.save_screenshot(screenshot_path_filename+'.png')
        # wait for webpage to be loaded
        #sleep(14)

        xpaths_of_energy_power = [f"//*[@id='item{x}']" for x in range(12)]
        '''
        for xpath_of_energy_power in xpaths_of_energy_power:
            self.logger.info(f"xpath: {xpath_of_energy_power}") 
        self.logger.info('*'*100)
        '''

        # things I want to collect
        #raw data
        str_update_YYMMDDHHMM = None
 
        # find update time, it's taiwan time zone
        xpath_update_YYMMDDHHMM_element ='//*[@id="datetime"]' 
        update_YYMMDDHHMM_element = driver.find_elements_by_xpath(xpath_update_YYMMDDHHMM_element) 
        str_update_YYMMDDHHMM = update_YYMMDDHHMM_element[0].text.strip()  
        self.logger.info(f"update timestamp : {str_update_YYMMDDHHMM }") 
        # convert time string to .....

        def get_rows_of_power_planets_and_power(targetXpath):
            #xpath_rows_plants_and_power = f"//*[@id='unitgentab']/tbody//tr[contains(@class,'group-item group-item--a-name-{energy_keyword}-b-')]" # not valid anymore
            list_rows_power_plant_power_elements = driver.find_elements_by_xpath(targetXpath)
            energy_name = None 
            array_rows_of_strings_plants_and_power = []
            for row in list_rows_power_plant_power_elements: 
                #self.logger.info(row.text) #this works
                self.logger.debug(len(row.find_elements(By.XPATH, './/a')))
                try:
                    # test if this row has a name attribute, which we want to get its value 
                    energy_name = row.find_element(By.XPATH, './/a').get_attribute("name")

                    # if new energy name is not None, skip to next row
                    self.logger.debug("energy_name: " + energy_name)
                    continue
                except Exception:
                    self.logger.debug('no <a> tag')
                # get data raw's text 
                row_unit_power_data = row.text.strip() 
                self.logger.debug(row_unit_power_data) #this works

                row_strings = None
                # we concatenate datetime and energy_name prefix with row string subtotal row 
                # then split by space to from array that we can later write to csv file
                if '小計' not in row_unit_power_data: 
                    row_strings = " ".join([str_update_YYMMDDHHMM, energy_name, row_unit_power_data]).split(" ")  
                    #self.logger.info(f"row_string: {row_strings}") 
                # add row_strings to array_rows_of_strings_plants_and_power except the last empty row
                if row_strings is not None:
                    array_rows_of_strings_plants_and_power.append(row_strings) 
                
            return array_rows_of_strings_plants_and_power 

        # the xpath of the table that we want to scrapy
        xpath_table_tbody_all_tr = f'//*[@id="unitgentab"]/tbody/tr'

        self.logger.info(f"start to gather table rows: {xpath_table_tbody_all_tr }" ) 
        ready_csv_data_strings = get_rows_of_power_planets_and_power(xpath_table_tbody_all_tr)
        row_count = len(ready_csv_data_strings) 
        self.logger.info(f"size of datat rows:   {row_count}" ) 
        assert row_count > 0 
        self.logger.info(f"end to gather table: " ) 
        """
         should be 222 rows with subtotal and last emptyrow, 
         209 rows in the total without subtotal and last empty row 
        """
        #self.logger.info(ready_csv_data_strings ) 


        # ToDo: take saving csv part to different file
        # write data to files
        # timestamp, plant_category, plant_name, plant_namespace_capacity, plant_generated_power_at_timestamp, power/namespace, PS, 

        filename_all_plants_power_output = "all_plants_power_output"
        # directory to save csv files, set to screenshot_dir,
        csv_files_path = screenshot_dir
        csv_filename_timestamp_all_plants_data =  start_time_string + "_all_plants_power_output.csv"
        
        #combine directory with filename to create file path
        csv_file_path = os.path.join(csv_files_path, csv_filename_timestamp_all_plants_data)

        self.logger.info(f"writing datat to csv_path_filename: {csv_file_path}")

        filename_total_power_ratio = "total_power_ratio_output"
        filename_total_power_ = "total_power_output"

        # ToDo: should we put header column into csv?
        # ToDo: test if we can open the path,
        with open(csv_file_path, 'a',) as csvfile:
            csvwriter = csv.writer(csvfile)
        # save the strings in each value into file filename_all_plants_power_output_without_subtotal_and_insert_date_time_plant_category 
            for string in ready_csv_data_strings:
                array_columns = string
                
                self.logger.info(f"creating json ")
                """
                 create json 
                 *ps is used cause ps can be None, and if it's not none it will be an array
                 so array_columns to csv seems to be a better idea?
                """
                yr_date, hr_minute, plant_category, plant, namespace_power, generated_power, percent, *ps = array_columns
                self.logger.info(f"yield json")
                yield {
                    
                    'yymmhh'    :   yr_date,
                    'hhmm'      :   hr_minute, 
                    'energy'    :   plant_category,
                    'name'      :   plant,
                    'namespace power' : namespace_power,
                    'generated power' : generated_power,
                    'percent'   :   percent,
                    #'comment'   :   unicode("".join(ps).encode('utf-8')),  
                    #'comment'   :   "".join(ps).encode('utf-8').decode('utf-8'),  
                    # cause ps is an array
                    'comment'   :   "".join(ps),  
                }
                #str(key) is the category of power, nuclrear, coal, LNG...etc
                ###   end of create json 
                self.logger.info(f"done creating json, back from yield ")


                self.logger.debug(f"array_columns : {array_columns }")
                csvwriter.writerow(array_columns) 
            self.logger.info(f"done writing to csv")

        # how to accumulate new data with old ones

        end_time = datetime.now(tz=timezone.utc)
        self.logger.info(f"parser ran {end_time - start_time}")
        
        driver.quit()
