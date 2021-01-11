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
        we take screenshot not when the data is updated
        usually the time that data is updated is 10mins earlier than the 
        time we take screenshot
        '''
        screenshot_filename = start_time_string + 'screenshot'
        '''
        screenshot will be saved in a folder called (relative path)screenshot_dir under current directory
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

        # download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
        # the version of the driver must match the version of chrome installed to work

        # instantiate a chrome options object so you can set the size and headless preference
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--window-size=1024X7373")
        chrome_options.add_argument("--window-size=1280x9216")

        # comment out the following line if you don't want to actually show Chrome instance
        # but you can still see that the crawling is working via output in console

        # chrome_options.add_argument("--headless")


        # comment out the following two lines to setup ProxyMesh service
        # make sure you add the IP of the machine running this script to you ProxyMesh account for IP authentication
        # IP:PORT or HOST:PORT you get this in your account once you pay for a plan

        # PROXY = "us-wa.proxymesh.com:31280"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)

        #print(chrome_driver_path+ '*'*10 )
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
        URL_IFRAME_TAIPOWER_ENERGY_UPDATED_EVERY_10MIN = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html"
        driver.get(URL_IFRAME_TAIPOWER_ENERGY_UPDATED_EVERY_10MIN) 

        # cause I want to fix some screenshot doesn't contain the 2nd part of the webpage and also didn't get the info of power generation by each plants
        timeout = 10
        xpath_nuclear_group_title_element = '//*[@id="group-id-unitgentab_-a-name-nuclear-a-b-核能-nuclear-b-"]/td/b'
        element_presence = ec.presence_of_element_located((By.XPATH, xpath_nuclear_group_title_element))
        nuclear_group_titel_element = WebDriverWait(driver, timeout).until(element_presence)
        # end of wait til 2nd part of the webpage's first nuclear  element to show up 
        



        # take screeshot of the screen 
        driver.save_screenshot(screenshot_path_filename+'.png')
        #driver.save_screenshot_as_png(screenshot_path_filename)

        ''' original URL
        driver.get("https://www.taipower.com.tw/tc/page.aspx?mid=206&cid=406&cchk=b6134cc6-838c-4bb9-b77a-0b0094afd49d")
        '''
        #driver.get('https://dribbble.com/designers')
        # wait for webpage to be loaded
        sleep(14)

        xpaths_of_energy_power = [f"//*[@id='item{x}']" for x in range(12)]
        '''
        for xpath_of_energy_power in xpaths_of_energy_power:
            self.logger.info(f"xpath: {xpath_of_energy_power}") 
        self.logger.info('*'*100)
        '''

        POST_xpath_of_energy_title  = "preceding-sibling::strong[1]"
        # things I want to collect
        dict_energy_power_plants_info_without_subtotal = {}
        array_str_power_plants_and_their_power_without_subtotal = []
        #raw data
        dict_energy_power = {}
        dict_energy_ratio = {}
        dict_energy_power_plants_info = {}
        str_total_power = None
        str_update_YYMMDDHHMM = None
        array_str_power_plants_and_their_power = []
 
        def write_array_to_file(filename, array_for_write):
            with open(filename, 'a') as f:
                for row in array_for_write:
                    # add datetime as prefix of each row?
                    # add plant category as postfix of each row?
                    f.write(row)
                    f.write('\n')



        # find update time, it's taiwan time zone
        xpath_update_YYMMDDHHMM_element ='//*[@id="datetime"]' 
        update_YYMMDDHHMM_element = driver.find_elements_by_xpath(xpath_update_YYMMDDHHMM_element) 
        str_update_YYMMDDHHMM = update_YYMMDDHHMM_element[0].text.strip()  
        self.logger.info('*'*100)
        self.logger.info(f"str_update_YYMMDDHHMM : {str_update_YYMMDDHHMM }") 
        # convert time string to .....

        # find total power generated
        total_power_element = driver.find_elements_by_xpath('//*[@id="nestSumId"]')
        str_total_power = total_power_element[0].text.strip() 
        self.logger.info('*'*100)
        self.logger.info(f"str_total_power : {str_total_power }") 

        
        # find energy and its ratio cause I want to verify it myself
        dict_xpaths_energy_ratio = {
                "nuclear":      "/html/body/div[2]/div[3]/div[1]/div/div[1]/span",
                "coal":         "/html/body/div[2]/div[3]/div[1]/div/div[2]/span",
                "co_gen":       "/html/body/div[2]/div[3]/div[1]/div/div[3]/span",
                "ipp_coal":     "/html/body/div[2]/div[3]/div[1]/div/div[4]/span",
                "ipp_lng":      "/html/body/div[2]/div[3]/div[1]/div/div[5]/span",
                "lng":          "/html/body/div[2]/div[3]/div[1]/div/div[6]/span",
                "oil":          "/html/body/div[2]/div[3]/div[2]/div/div[1]/span",
                "diesel":       "/html/body/div[2]/div[3]/div[2]/div/div[2]/span",
                "hydro":        "/html/body/div[2]/div[3]/div[2]/div/div[3]/span",
                "wind":         "/html/body/div[2]/div[3]/div[2]/div/div[4]/span",
                "solar":        "/html/body/div[2]/div[3]/div[2]/div/div[5]/span",
                "pumping_gen":  "/html/body/div[2]/div[3]/div[2]/div/div[6]/span",
        }

        for key, value in dict_xpaths_energy_ratio.items():
            ratio_element = driver.find_elements_by_xpath(value)
            str_ratio = ratio_element[0].text.strip()  
            dict_energy_ratio[key] = str_ratio
        self.logger.info(f"dict_energy_ratio: {dict_energy_ratio}") 
        self.logger.info('*'*100)

        
        #def find_energy_title_and_power_and_ratio(xpath_of_energy_power):

        # this function will find the text of energy title and generated power the first part of the taipower power data report
        def find_energy_title_and_power(xpath_of_energy_power):
            gen_power_element = driver.find_elements_by_xpath(xpath_of_energy_power) 
            str_gen_power = gen_power_element[0].text.strip()
            xpath_of_energy_title = xpath_of_energy_power + '/' + POST_xpath_of_energy_title
            '''
            self.logger.info('*'*100)
            self.logger.info(f"xpath_of_energy_title: {xpath_of_energy_title}") 
            '''
            energy_title_element = driver.find_elements_by_xpath(xpath_of_energy_title ) 
            str_energy_title= energy_title_element[0].text.strip() 
            '''
            self.logger.info(f"string energy: {str_energy_title}") 
            self.logger.info(f"energy power: {str_gen_power}") 
            '''

            return {str_energy_title : str_gen_power}
            #return {"{str_energy_title}" : f"{str_gen_power}"}


        # find all energy power pair 
        for xpath_of_energy_power in xpaths_of_energy_power:
            dict_energy_power.update(find_energy_title_and_power(xpath_of_energy_power))
        assert len(dict_energy_power) == 12
        self.logger.info('*'*100)
        self.logger.info(dict_energy_power)

        # find all power plants and its generated power  categorized by energy type
               
        xpath_nuclear_title = '//*[@id="group-id-unitgentab_-a-name-nuclear-a-b-核能-nuclear-b-"]/td/b'
        xpath_coal_title = '//*[@id="group-id-unitgentab_-a-name-coal-a-b-燃煤-coal-b-"]/td/b'
        xpath_co_gen_title = '//*[@id="group-id-unitgentab_-a-name-cogen-a-b-汽電共生-co-gen-b-"]/td/b'
        xpath_IPP_coal_title = '//*[@id="group-id-unitgentab_-a-name-ippcoal-a-b-民營電廠-燃煤-ipp-coal-b-"]/td/b'
        xpath_LNG_title = '//*[@id="group-id-unitgentab_-a-name-lng-a-b-燃氣-lng-b-"]/td/b'
        xpath_IPP_LNG_title = '//*[@id="group-id-unitgentab_-a-name-ipplng-a-b-民營電廠-燃氣-ipp-lng-b-"]/td/b'
        xpath_oil_title = '//*[@id="group-id-unitgentab_-a-name-oil-a-b-燃油-oil-b-"]/td/b'
        xpath_diesel_title = '//*[@id="group-id-unitgentab_-a-name-diesel-a-b-輕油-diesel-b-"]/td/b'
        xpath_hydro_title = '//*[@id="group-id-unitgentab_-a-name-hydro-a-b-水力-hydro-b-"]/td/b'
        xpath_wind_title = '//*[@id="group-id-unitgentab_-a-name-wind-a-b-風力-wind-b-"]/td/b'
        xpath_wind_title = '//*[@id="group-id-unitgentab_-a-name-solar-a-b-太陽能-solar-b-"]/td/b'
        xpath_pumping_gen_title =   '//*[@id="group-id-unitgentab_-a-name-pumpinggen-a-b-抽蓄發電-pumping-gen-b-"]/td/b'
        xpath_pumping_load_title =  '//*[@id="group-id-unitgentab_-a-name-pumpingload-a-b-抽蓄負載-pumping-load-b-"]/td/b'
        xpath_geothermal_title =    '//*[@id="group-id-unitgentab_-a-name-geothermal-a-b-地熱-geothermal-b-"]/td/b'

        '''
        xpath_nuclear_title_element = driver.find_elements_by_xpath(xpath_nuclear_title ) 
        str_nuclear_title = xpath_nuclear_title_element[0].text.strip() 
        self.logger.info(f'nuclear title: {str_nuclear_title}')
        assert 'nuclear' in str_nuclear_title.lower()
        self.logger.info('~'*100)
        #1st nuclear plant and power generated row//*[@id="unitgentab"]/tbody/tr[2]
        '''

        power_plant_and_generated_power_keywords = {
                "nuclear":      "nuclear-a-b-核能-nuclear",
                "coal":         "coal-a-b-燃煤-coal",
                "co_gen":       "cogen-a-b-汽電共生-co-gen",
                "ipp_coal":     "ippcoal-a-b-民營電廠-燃煤-ipp-coal",
                "ipp_lng":      "ipplng-a-b-民營電廠-燃氣-ipp-lng",
                "lng":          "lng-a-b-燃氣-lng",
                "oil":          "oil-a-b-燃油-oil",
                "diesel":       "diesel-a-b-輕油-diesel",
                "hydro":        "hydro-a-b-水力-hydro",
                "wind":         "wind-a-b-風力-wind",
                "solar":        "solar-a-b-太陽能-solar",
                "pumping_gen":  "pumpinggen-a-b-抽蓄發電-pumping-gen",
                "pumping_load": "pumpingload-a-b-抽蓄負載-pumping-load",
                "geothermal":   "geothermal-a-b-地熱-geothermal"
        }
        # should try each category and make sure getting all the rows in each category before we try to grab all categories
        def get_rows_of_power_planets_and_power(energy_keyword):
            xpath_rows_plants_and_power = f"//*[@id='unitgentab']/tbody//tr[contains(@class,'group-item group-item--a-name-{energy_keyword}-b-')]"
            # cannot use array cause pumping gen will overwrite pumping load
            # use dictionary?
            # shall we remove subtotal rows of each category?
            array_rows_of_strings_plants_and_power = []

            rows_power_plant_power_elements = driver.find_elements_by_xpath(xpath_rows_plants_and_power) 
                
            array_rows_of_strings_plants_and_power = \
                [x.text.strip() for x in rows_power_plant_power_elements]
                #[x.text.strip() for x in rows_power_plant_power_elements if "小計" not in x.text ]

            return array_rows_of_strings_plants_and_power 

        # loop through power_plant_and_generated_power_keywords 
        # to get all the strings of rows of all power plants and generated power
        # passed: all rows are extracted
        #test the power plants in nuclear plant category
        rows_count = 0
        '''
        if power_plant_and_generated_power_keywords['nuclear'] is not None:
            array_str_power_plants_and_their_power = get_rows_of_power_planets_and_power(power_plant_and_generated_power_keywords['nuclear'])
        else:
            self.logger.info(f"key not found in dict")

        self.logger.info(f"array_str_power_plants_and_their_power:{array_str_power_plants_and_their_power }")
        self.logger.info('~'*100)
        '''
        # wait til 2nd part of the webpage's first nuclear  element to show up 
                # might want to save different categories to diff files/tables
        for key, value in power_plant_and_generated_power_keywords.items(): 
            self.logger.info(f"key:{key}") 
            array_str_single_category_power_plants_and_their_power = get_rows_of_power_planets_and_power(value) 
            rows_count += len(array_str_single_category_power_plants_and_their_power) 
            # the value of each key is actually an list of strings
            dict_energy_power_plants_info[key] = array_str_single_category_power_plants_and_their_power 

        self.logger.info(f"dict_energy_power_plants_info: {dict_energy_power_plants_info}")
            #self.logger.info("rows of power plants and generated power")
            #self.logger.info(f"{len(array_str_power_plants_and_their_power)} rows") 
            #self.logger.info(array_str_power_plants_and_their_power)

        # so far we have 220 rows, including the subtitle rows in each categories
        # 220 can be changed if more power plants show up
        """
        self.logger.info(len(array_str_power_plants_and_their_power)) 
        self.logger.info(array_str_power_plants_and_their_power ) 
        self.logger.info('~'*100)
        """
        self.logger.info(len(dict_energy_power_plants_info)) 
        #assert 13 == len(dict_energy_power_plants_info)
        self.logger.info(f'row count:{rows_count}')
        #assert rows_count == 208 without geothermal
        #assert rows_count == len(dict_energy_power_plants_info) 

        # remove subtotal rows from dict_energy_power_plants_info's value
        # and add date time and key to each string(plant row)
        for key, value in dict_energy_power_plants_info.items():
            #array_plants = [item for item in value if '小計' not in item]
            # remove subtotal string, add date, time and key(plant category) to each string
            array_plants = [str_update_YYMMDDHHMM + ' ' + str(key) + ' ' + item for item in value if '小計' not in item]
            dict_energy_power_plants_info_without_subtotal[key] = array_plants
        self.logger.info(f"dict_energy_power_plants_info_without_subtotal : {dict_energy_power_plants_info_without_subtotal}")
        self.logger.info('~'*100)

        # ToDo: take saving csv part to different file
        # write data to files
        # timestamp, plant_category, plant_name, plant_namespace_capacity, plant_generated_power_at_timestamp, power/namespace, PS, 

        # save each string in each value fo  dict_energy_power_plants_info_without_subtotal to a file(csv)
        filename_all_plants_power_output = "all_plants_power_output"
        # directory to save csv files, set to screenshot_dir,
        csv_files_path = screenshot_dir
        # we will save dict_energy_power_plants_info_without_subtotal to it
        # this csv file contains rows of power plant data and the time we recorded 
        #filename_all_plants_power_output_without_subtotal_and_insert_date_time_plant_category = "all_plants_power_output.csv"
        csv_filename_timestamp_all_plants_data =  start_time_string + "_all_plants_power_output.csv"
        
        #combine directory with filename to create file path
        csv_file_path = os.path.join(csv_files_path, csv_filename_timestamp_all_plants_data)

        self.logger.info(f"csv_path_filename: {csv_file_path}")
        #exit()

        filename_total_power_ratio = "total_power_ratio_output"
        filename_total_power_ = "total_power_output"

        # ToDo: should we put header column into csv?
        # ToDo: test if we can open the path,
        import csv
        with open(csv_file_path, 'a',) as csvfile:
            csvwriter = csv.writer(csvfile)
        # save the strings in each value into file filename_all_plants_power_output_without_subtotal_and_insert_date_time_plant_category 
            for key, value in dict_energy_power_plants_info_without_subtotal.items():
                data_strings = value
                for string in data_strings:
                    array_columns = string.split(' ')
                    
                    ###  create json 
                    # *ps is used cause ps can be None, and if it's not none it will be an array
                    # so array_columns to csv seems to be a better idea?
                    yr_date, hr_minute, plant_category, plant, namespace_power, generated_power, percent, *ps = string.split(' ') 
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

                    self.logger.info(f"array_columns : {array_columns }")
                    csvwriter.writerow(array_columns) 
        # how to accumulate new data with old ones

        """
        write_array_to_file(filename_all_plants_power_output, array_str_power_plants_and_their_power)
        write_array_to_file(total_power_ratio_output, array_str_power_plants_and_their_power)
        write_array_to_file(total_power_output, array_str_power_plants_and_their_power)
        """

        
        '''
        # get P.S. part content
        xpath_rows_of_PS_content_table = "/html/body/div[2]/div[4]/div/table/tbody/tr"
        rows_of_PS_centent_table_elements = driver.find_elements_by_xpath(xpath_rows_of_PS_content_table) 

        self.logger.info(f"numbers of PS rows: {len(rows_of_PS_centent_table_elements)}")
        #get the text content of all PS rows but with '\n' in between chars
        array_rows_of_PS_centent_table_texts = [x.text.strip() for x in rows_of_PS_centent_table_elements]

        self.logger.info(array_rows_of_PS_centent_table_texts)
        self.logger.info('~'*100)
        # save PS conent to a table?
        # save total power of each category to database?
        # save each power of each category of each power plant to database?
        '''

        
        ''' 2021 Jan 04 since our browser size is the same as the webpage content, we 
        don't need to deal with scrolling!

        self.logger.info("*********** before scrolling ************")
        self.logger.info(scrapy_selector.css('.vcard a[data-subject]::text').getall())
        self.logger.info(len(scrapy_selector.css('.vcard a[data-subject]::text').getall()))

        # designer page with an infinite scroll
        last_height = driver.execute_script("return document.body.scrollHeight")
        SCROLL_PAUSE_TIME = 5
        MAX_SCROLL = 10
        i = 0
        while i <= MAX_SCROLL:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            i += 1
            # IMPORTANT!!!
            # you have to get the selector again after each scrolling
            # in order to get the newly loaded contents
            scrapy_selector = Selector(text = driver.page_source)
            self.logger.info("*********** during scrolling ************")
            self.logger.info("Total scrolls executed: {}".format(i))
            self.logger.info("this is the current designer names extracted: {}".format(scrapy_selector.css('.vcard a[data-subject]::text').getall()))
            self.logger.info("Total names extracted: {}".format(len(scrapy_selector.css('.vcard a[data-subject]::text').getall())))

            sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        self.logger.info("*********** scrolling done ************")
        self.logger.info("final designer names extracted: {}".format(scrapy_selector.css('.vcard a[data-subject]::text').getall()))
        self.logger.info("Final total names extracted: {}".format(len(scrapy_selector.css('.vcard a[data-subject]::text').getall())))

        '''
        end_time = datetime.now(tz=timezone.utc)
        self.logger.info(f"parser ran {end_time - start_time}")
        
        driver.quit()
