from importlib.metadata import metadata
import json
from random import randint, random
from termios import CSTART
from requests import TooManyRedirects, options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.service import Service as BraveService
# from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.service import Service as BraveService
# from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import psycopg2
import undetected_chromedriver as uc

db_values = {
    'book1': {
        'name': 'NNNNNN',
        'reviews': '9.8',
        'chapters': 32,
        'last_checked_chapter': 21 
    },'book2': {
        'name': 'OOOOOO',
        'reviews': '9.3',
        'chapters': 88,
        'last_checked_chapter': 87 
    },'book1': {
        'name': 'NNNNNN',
        'reviews': '9.9',
        'chapters': 65,
        'last_checked_chapter': 65 
    },
}

# Function To Custom Log Data On The Console
def custom_log(msg):
    print('='*50)
    print('\n', msg)
    print('\n')
###########################################

def write_to_db(json_data):
    try:
        connection = psycopg2.connect(user="postgres", password='tester', host="127.0.0.1", port="5432", database="test2manua")
        cursor = connection.cursor()

        custom_log('Trying Cursor Excecution')

        sql_statement = '''
            INSERT INTO comics (title, description, released, author, serialization, posted_by, posted_on, updated_on, artist, type, ratings, image_link, followed_by, status, keywords, first_chapter, last_chapter, related_series, is_popular_daily, is_popular_weekly, is_popular_monthly, is_popular_all, is_featured, is_trending)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (title) DO UPDATE SET
            (title, description, released, author, serialization, posted_by, posted_on, updated_on, artist, type, ratings, image_link, followed_by, status, keywords, first_chapter, last_chapter, related_series, is_popular_daily, is_popular_weekly, is_popular_monthly, is_popular_all, is_featured, is_trending) = (EXCLUDED.title, EXCLUDED.description, EXCLUDED.released, EXCLUDED.author, EXCLUDED.serialization, EXCLUDED.posted_by, EXCLUDED.posted_on, EXCLUDED.updated_on, EXCLUDED.artist, EXCLUDED.type, EXCLUDED.ratings, EXCLUDED.image_link, EXCLUDED.followed_by, EXCLUDED.status, EXCLUDED.keywords, EXCLUDED.first_chapter, EXCLUDED.last_chapter, EXCLUDED.related_series, EXCLUDED.is_popular_daily, EXCLUDED.is_popular_weekly, EXCLUDED.is_popular_monthly, EXCLUDED.is_popular_all, EXCLUDED.is_featured, EXCLUDED.is_trending);
        '''
        item = json_data
        custom_log("Trying Statement Execution")
        try:
            custom_log('Trying To Execute')
            cursor.execute(sql_statement, (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12], item[13], item[14], item[15], item[16], item[17], item[18], item[19], item[20], item[21], item[22], item[23]))
            custom_log('Trying To Commit')
            connection.commit()
        except Exception as e:
            custom_log(e)

    except (Exception, psycopg2.Error) as error:
        print('Failed With Error ', error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


    try:
        connection = psycopg2.connect(user="postgres", password='tester', host="127.0.0.1", port="5432", database="test2manua")
        cursor = connection.cursor()

        for item in json_data:
            select_statement = 'select id from comics where title = \'{0}\''.format(item["title"])

            cursor.execute(select_statement)

            row = cursor.fetchone()
            print(row)
            comic_id = row[0]
            for chapter in item[18]:
                print('Comic Id: ', comic_id)
                images = ''
                for image in chapter[3]:
                    images += image
                    images += ', '
                

                select_statement = 'select id from chapters where num = \'{0}\' and comic_id = \'{1}\''.format(chapter[0], comic_id)

                cursor.execute(select_statement)

                row = cursor.fetchone()
                chapters_statement = """
                INSERT INTO chapters (id, num, release, images, tags, comic_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                (id, num, release, images, tags, comic_id) = (EXCLUDED.id, EXCLUDED.num, EXCLUDED.release, EXCLUDED.images, EXCLUDED.tags, EXCLUDED.comic_id);"""
                cursor.execute(chapters_statement, (row[0], chapter[0], chapter[2], images, chapter[1], comic_id))
                connection.commit()
            
            for genre in item['genres']:

                select_statement = 'select id from genres where name = \'{0}\' and comic_id = \'{1}\''.format(genre, comic_id)

                cursor.execute(select_statement)

                row = cursor.fetchone()
                genre_statement = """
                INSERT INTO genres (id, name, comic_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                (id, name, comic_id) = (EXCLUDED.id, EXCLUDED.name, EXCLUDED.comic_id);"""
                cursor.execute(genre_statement, (row[0], genre, comic_id))
                connection.commit()
            


    except (Exception, psycopg2.Error) as error:
        print('Failed With Error ', error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


#############################################
#                                           #
#           Function To Read Save           #
#            And Cycle Chapters             #
#                                           #
#############################################

def read_chapters(nav_type, chapter_number):
    chapter_object = []
    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################  

    if nav_type == 'Init':
        try:
            article = driver.find_element(By.TAG_NAME, 'article')
            next_button = article.find_element(By.CLASS_NAME, 'ch-next-btn')
            custom_log(next_button)
        except:
            custom_log('Trying To Move To Next Chapter')
    else:
        try:
            article = driver.find_element(By.TAG_NAME, 'article')
            next_button = article.find_element(By.CLASS_NAME, 'ch-next-btn')
            custom_log(next_button)
        except:
            custom_log('Trying To Move To Next Chapter')
        
        try:
            next_link = next_button.get_attribute('href')
            driver.get(next_link)
        except:
            custom_log('Navigating To Next Chapter First')

    
    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    custom_log("Retrieving Reading Area!")

    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    try:
        article = driver.find_element(By.TAG_NAME, 'article')
        images = article.find_elements(By.TAG_NAME, 'img')
        custom_log(images)
        custom_log(len(images))
    except:
        custom_log('Tried Getting Messages. Now Saving Them')


    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    image_db = './Images.txt'


    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    with open(image_db,'a') as file:
        file.write(chapter_number)
        file.write('\n')
        file.close()
    custom_log("Attempting Saving Images To DB!")
    images_list = []
    for image in images:
        image_link = image.get_attribute('src')
        images_list.append(image_link)
        image_storage = str(image) + str(series_title)
        with open(image_db,'a') as file:
            file.write(image_storage)
            file.write('\n')
            file.close()


    date_released = driver.find_element(By.CLASS_NAME, 'entry-date')
    date_obj = date_released.get_attribute('datetime')

    chapter_tags = driver.find_element(By.CLASS_NAME, 'chaptertags')
    chapter_element = chapter_tags.find_element(By.TAG_NAME, 'p').text.replace('tags:', '')

    custom_log("Images Saved To DB!")

    chapter_obj = {
            "num": chapter_number,
            "tags": chapter_element,
            "release": date_obj,
            "images":images_list
        }

    chapter_object.append(chapter_obj)

    custom_log('Going To While')


    chapter_index = chapter_list.index(chapter_number)
    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    custom_log("Moving To Next Chapter If Available!")
    while 'disabled' not in next_button.get_attribute('class'):
        custom_log("Next Chapter Still Available. Moving Forward!")

        ##############################################################
        # Get The Article & Next Button Elements In The Chapter Page #
        ##############################################################
        try:
            next_link = next_button.get_attribute('href')
            driver.get(next_link)
            custom_log('Next In While!')
        except:
            custom_log('Tried Clicking Next. Now Searchign For Reading Area.')
        
        chapter_index -= 1 
        ##############################################################
        # Get The Article & Next Button Elements In The Chapter Page #
        ##############################################################
        article = driver.find_element(By.TAG_NAME, 'article')
        images = article.find_elements(By.TAG_NAME, 'img')
        

        ##############################################################
        # Get The Article & Next Button Elements In The Chapter Page #
        ##############################################################
        image_db = './Images.txt'
        
        ##############################################################
        # Get The Article & Next Button Elements In The Chapter Page #
        ##############################################################
        images_list = []
        for image in images:
            image_link = image.get_attribute('src')
            images_list.append(image_link)
            image_storage = str(image_link) + str(series_title)
            with open(image_db,'a') as file:
                file.write(image_link)
                file.write('\n')
                file.close()

        try:
            date_released = driver.find_element(By.CLASS_NAME, 'entry-date')
            date_obj = date_released.get_attribute('datetime')
        except:
            custom_log('Moving To Tags Section')

        try:
            chapter_tags = driver.find_element(By.CLASS_NAME, 'chaptertags')
            tags_chapter = chapter_tags.find_element(By.TAG_NAME, 'p').text.replace('tags:', '')
        except:
            custom_log('Saving String')

        custom_log("Images Saved To DB!")

        chapter_number = chapter_list[chapter_index]
        
        chapter_obj = {
                "num": chapter_number,
                "tags": tags_chapter,
                "release": date_obj,
                "images": images_list
            }

        chapter_object.append(chapter_obj)

        custom_log(chapter_string)

        ##############################################################
        # Get The Article & Next Button Elements In The Chapter Page #
        ##############################################################
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'ch-next-btn')
        except:
            custom_log('Sleeping For Next Chapter')
            time.sleep(5)
            custom_log('Going To Next Chapter')

    try:
        try:
            if series_artist == None:
                series_artist = '-'
        except:
            series_artist = '-'

        try:
            resulting_json = {
                "title": series_title,
                "description": series_description,
                "released": series_released,
                "author": series_author,
                "serialization": series_serialization,
                "posted_by": series_posted_by,
                "posted_on": series_posted_on,
                "updated_on": series_updated_on,
                "artist": series_artist,
                "type":series_type,
                "ratings": float(series_rating),
                "image_link": series_cover_image,
                "followed_by": int(series_followed_by),
                "genres": series_genres,
                "status": series_status,
                "keywords": series_keywords,
                "first_chapter": series_last_chapter,
                "last_chapter": series_first_chapter,
                "chapters": chapter_object,
                "related_series": related_series, 
                "is_popular_daily": is_popular_daily,
                "is_popular_weekly": is_popular_weekly,
                "is_popular_monthly": is_popular_monthly,
                "is_popular_all": is_popular_all,
                "is_featured": is_featured,
                "is_trending": is_trending
            }
        except Exception as e:
            custom_log(e)


        # try:
        #     custom_log("Loading JSON String Into Loads")
        #     resulting_json = json.loads(resulting_json)
        # except Exception as e:
        #     custom_log(e)

        try:
            custom_log('Attempting Write To File')
            with open("new_series.json", "w") as write_file:
                json.dump(resulting_json, write_file, indent=4)
        except Exception as e:
            custom_log(e)
        custom_log(resulting_json)

        try:
            write_to_db(resulting_json)
            custom_log('Data Save Successfully')
        except Exception as e:
            custom_log(e)
            custom_log('Something Went Wrong In The DB')
    except Exception as e:
        custom_log(e)
        custom_log('DB Minght Not Be Written')

    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    try:
        driver.get(list_url)
    except Exception as e:
        custom_log(e)
        custom_log('Trying To Return To List Page')
        try:
            custom_log('Retying To Return To List Page')
        except:

            driver.get(list_url)


#############################################
#                                           #
#          Function To Check First          #
#           Chapter To Be Clicked           #
#                                           #
#############################################

def check_chapters(chapter_param):
    global driver, series_title, series_description, series_released, series_author, series_serialization, series_posted_by, series_posted_on, series_updated_on, series_artist, series_type, series_rating, series_cover_image, series_followed_by, genres, series_status, series_keywords, series_last_chapter, series_first_chapter, related_series, is_popular, is_featured, is_trending, trending_series, features, popular_all, popular_monthly, popular_weekly, popular_daily, is_popular_daily, is_popular_weekly, is_popular_monthly, is_popular_all, chapter_string, chapter_list
    if chapter_param == 'New':
        try:
            chapter_container = driver.find_element(By.CLASS_NAME, 'clstyle')
            chapters_all = chapter_container.find_elements(By. TAG_NAME, 'li')
        except:
            custom_log('Trying To Look At First Chapter')

        chapter_list = []

        for chapter in chapters_all:
            chapter_attr = chapter.get_attribute('data-num')
            chapter_list.append(chapter_attr)
        try:
            custom_log("Looking For First Chapter To Visit!")
            first_chapter = chapters_all[-1]
            first_chapter_num = str(first_chapter.get_attribute('data-num'))
            custom_log('First Chapter Is ' + first_chapter_num)
            first_chapter_link = first_chapter.find_element(By.TAG_NAME, 'a').get_attribute('href')
            try:
                driver.get(first_chapter_link)
                custom_log('Navigating To First Chapter')
            except:
                custom_log('Trying To View First Chapter')
            custom_log("Opening First Chapter!")
            read_chapters('Init', first_chapter_num)
        except Exception as e:
            custom_log(e)
            custom_log("Not Fully Read All Chapters")
    else:
        try:
            chapter_container = driver.find_element(By.CLASS_NAME, 'clstyle')
            chapters_all = chapter_container.find_elements(By. TAG_NAME, 'li')
        except:
            custom_log('Trying To Look At First Chapter')

        chapter_list = []

        for chapter in chapters_all:
            chapter_attr = chapter.get_attribute('data-num')
            chapter_list.append(chapter_attr)

        for chapter in chapters_all:
            if chapter.text == chapter_param:
                last_checked_chapter_element = chapter
                break
        
        try:
            last_checked_chapter_num = str(last_checked_chapter_element.get_attribute('data-num'))
            custom_log('Last Checked Chapter Is ' + last_checked_chapter_num)
            try:
                last_checked_link = last_checked_chapter_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
                driver.get(last_checked_link)
            except:
                custom_log('Trying To Move To Last Chapter')
            custom_log("Opening Last Checked Chapter Chapter!")
        except:
            custom_log("Moving To Chapter Details")

        try:
            read_chapters('Next', last_checked_chapter_num)
        except:
            custom_log('Not All Chapters Are Read')


    ##############################################################
    # Get The Article & Next Button Elements In The Chapter Page #
    ##############################################################
    

db_list_of_series = ''


#############################################
#                                           #
#           Function To Read Comic          #
#              Details & Data               #
#                                           #
#############################################

def check_comics():
    global actions
    global list_url
    global driver, series_title, series_description, series_released, series_author, series_serialization, series_posted_by, series_posted_on, series_updated_on, series_artist, series_type, series_rating, series_cover_image, series_followed_by, series_genres, series_status, series_keywords, series_last_chapter, series_first_chapter, related_series, is_featured, is_trending, trending_series, features, popular_all, popular_monthly, popular_weekly, popular_daily, is_popular_daily, is_popular_weekly, is_popular_monthly, is_popular_all, chapter_string


    ########################################################
    # Get Container Element Holding The List Of All Comics #
    ########################################################
    try:
        list_container = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div[1]/div/div[2]/div[5]')))
    except:
        custom_log('Trying Scroliing Into View')
    

    ################################################
    # Search For All Comics In The List Container  #
    ################################################
    try:
        driver.execute_script("arguments[0].scrollIntoView()", list_container)
        all_series = list_container.find_elements(By.CLASS_NAME, 'series')
        custom_log(all_series)
        custom_log("Got All Anchor Tags To Series!")
    except:
        custom_log('Trying To Move Into Links')


    #################################
    # Get The URL Of The Lists Page #
    #################################
    list_url = driver.current_url


    ############################################################
    # Loop Though All Comics In The List And Get Their Details #
    ############################################################
    for series in all_series:
        global chapter_string
        custom_log('Current Series Is ' + series.text)
        title = series.text
        chapter_string = ''
        series_title = title

        ############################################
        # Check If Series Title Exists In DataBase #
        ############################################

        try:
            series_link = series.get_attribute('href')
            driver.get(series_link)
            custom_log('Clicked On Series')
        except Exception as e:
            custom_log(e)
            custom_log('Trying To Open Series')

        try:
            connection = psycopg2.connect(user="postgres", password='tester', host="127.0.0.1", port="5432", database="test2manua")
            cursor = connection.cursor()
            select_statement = 'select title from comics;'

            cursor.execute(select_statement)

            database_data = cursor.fetchall()

        except (Exception, psycopg2.Error) as error:
            custom_log(error)

        finally:
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
                custom_log('Values From DB Not Checked')
        #######################################################
        if title not in database_data:
            custom_log('Add Series To Db')


            custom_log("Opening Series...")
            ##############################################################
            # Get All Details For The Series #
            ##############################################################


            ##############################################################
            # Get Get Title & Description Of Series #
            ##############################################################
            try:
                title_element = driver.find_element(By.CLASS_NAME, 'entry-title')
                series_title = title_element.text
                custom_log(series_title)
                description_element = driver.find_element(By.CLASS_NAME, 'entry-content')
                series_description = description_element.text
                custom_log(series_description)
            except:
                custom_log("Attempting To Get Series MetaData & Details")


            if series_title == trending_series:
                is_trending = True
            else:
                is_trending = False

            if series_title in features:
                is_featured = True
            else:
                is_featured = False

            if series_title in popular_all:
                is_popular_all = True
            else:
                is_popular_all = False
            if series_title in popular_monthly:
                is_popular_monthly = True
            else:
                is_popular_monthly = False
            if series_title in popular_weekly:
                is_popular_weekly = True
            else:
                is_popular_weekly = False
            if series_title in popular_daily:
                is_popular_daily = True
            else:
                is_popular_daily = False
            

            ##############################################################
            # Get Series MetaData Like Release, Author & The Rest #
            ##############################################################
            try:
                all_details = driver.find_elements(By.CLASS_NAME, 'flex-wrap')
                for detail in all_details:    
                    details = detail.find_elements(By.CLASS_NAME, 'fmed')
                    for data in details:
                        data1 = data.find_element(By.TAG_NAME, 'b')
                        data2 = data.find_element(By.TAG_NAME, 'span')
                        dt1 = data1.text
                        dt2 = data2.text
                        if dt1.lower() == "released": 
                            series_released = dt2
                        elif dt1.lower() == "author":
                            series_author = dt2
                        elif dt1.lower() == "serialization":
                            series_serialization = dt2
                        elif dt1.lower() == "posted by":
                            series_posted_by = dt2
                        elif dt1.lower() == "posted on":
                            series_posted_on = dt2
                        elif dt1.lower() == "updated on":
                            series_updated_on = dt2
                        elif dt1.lower() == "artist":
                            series_artist = dt2
                        elif dt1.lower() == "type":
                            series_type = dt2
                        else:
                            data_pair = {dt1: dt2}
                            custom_log(data_pair)
            except:
                custom_log('Attempting To Move To Chapter Details For Series')

            try:
                if series_artist:
                    pass
                else:
                    series_artist = '-'
            except:
                series_artist = '-'


            ##############################################################
            # Get Series' Genres As A List #
            ##############################################################
            series_genres = []
            try:
                genre_element = driver.find_element(By.CLASS_NAME, 'mgen')
                genres_list = genre_element.find_elements(By.TAG_NAME, 'a')
                for genre in genres_list:
                    series_genres.append(genre.text)
                custom_log(series_genres)
            except:
                custom_log('Fetching Next Detail')

            
            ##############################################################
            # Get Number Of Followers For Series #
            ##############################################################
            try:
                followed_by_element = driver.find_element(By.CLASS_NAME, 'bmc')
                followed_by_string = followed_by_element.text
                custom_log(followed_by_string)
                try:
                    followed_by = re.findall(r'\b\d{1,3}(?:,\d{3})*(?!\d)', followed_by_string)
                    series_followed_by = int(followed_by[0].replace(',', ''))
                except:
                    regex_value = re.findall(r'\d+', followed_by_string)
                    digits_list = list(map(int, regex_value))
                    followed_by = digits_list[0]
                    series_followed_by = int(followed_by)
                custom_log(series_followed_by)
            except Exception as e:
                custom_log(e)
                custom_log('Fetching Next Detail')


            ##############################################################
            # Get Series Rating #
            ##############################################################
            try:
                rating_element = driver.find_element(By.CLASS_NAME, 'rating-prc')
                rating_no_element = rating_element.find_element(By.CLASS_NAME, 'num')
                series_rating = rating_no_element.text
                custom_log(series_rating)
            except:
                custom_log('Fetching Next Detail')


            ##############################################################
            # Get Status & Type Values As Key:Value Pairs #
            ##############################################################
            try:
                meta_list = driver.find_elements(By.CLASS_NAME, 'imptdt')
                for item in meta_list:
                    text = item.text
                    if 'type' in text.lower():
                        series_type = text.replace('Type', '')
                        custom_log(series_type)
                    elif 'status' in text.lower():
                        series_status = text.replace('Status', '')
                        custom_log(series_status)
                    else:
                        meta = {text[0]: text[1]}
                        custom_log(meta)
            except Exception as e:
                custom_log(e)
                custom_log('Fetching Next Detail')


            ##############################################################
            # Get Keywords Used For Series #
            ##############################################################
            try:
                series_element = driver.find_element(By.CLASS_NAME, 'animefull')
                keywords_list = series_element.find_element(By.CLASS_NAME, 'bottom')
                keywords = keywords_list.text
                series_keywords = keywords.replace('keywords:', '')
                custom_log(series_keywords)
            except:
                custom_log('Fetching Next Detail')


            ##############################################################
            # Get Related Articles For Series #
            ##############################################################
            related_series = ''
            try:
                releases_elements = driver.find_element(By.CLASS_NAME, 'listupd')
                custom_log(releases_elements)
                # related_series_element = releases_elements[-2]
                # custom_log(related_series_element)
                all_related_series = releases_elements.find_elements(By.CLASS_NAME, 'tt')
                custom_log(all_related_series)
                for series in all_related_series:
                    related_series += series.text 
                    related_series += ','
                custom_log(related_series)
                if related_series == '':
                    related_series = 'No Comics'
            except:
                custom_log('Fetching Next Detail')


            ##############################################################
            # Get Chapter Details ( First  &  Last Chapters) #
            ##############################################################

            chapter_list = []
            try:
                chapter_container = driver.find_element(By.CLASS_NAME, 'clstyle')
                custom_log("Checking Last Chapter!")
                chapters_all = chapter_container.find_elements(By. TAG_NAME, 'li')
                last_chapter = chapters_all[0].get_attribute('data-num')
                first_chapter = chapters_all[-1].get_attribute('data-num')
                series_last_chapter = last_chapter
                series_first_chapter = first_chapter
                custom_log('First Chapter Is ' + str(first_chapter) + ' & Last Chapter Is ' + str(last_chapter))
            except:
                custom_log('Moving To Simulation')
            

            ##############################################################
            # Get Series Cover Image #
            ##############################################################
            cover_for_cover_image = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumb')))
            series_cover_image = cover_for_cover_image.find_element(By.TAG_NAME, 'img').get_attribute('src')

            ##################################################################################
            # Proceed To Fetch Chapter Details. Pass 'New' Param To Check From First Chapter #
            ##################################################################################
            custom_log("Getting Ready To Check Series Chapters!")
            check_chapters('New')
        else:
            ##############################################################
            # Get Chapter Details ( First  &  Last Chapters) #
            ##############################################################
            try:
                chapter_container = driver.find_element(By.CLASS_NAME, 'clstyle')
                custom_log("Checking Last Chapter!")
                chapters_all = chapter_container.find_elements(By. TAG_NAME, 'li')
                last_chapter = chapters_all[0].get_attribute('data-num')
                first_chapter = chapters_all[-1].get_attribute('data-num')
                custom_log('First Chapter Is ' + str(first_chapter) + ' & Last Chapter Is ' + str(last_chapter))
            except:
                custom_log('Moving To Simulation')

            ##############################################################
            # Get Last Checked Chapter For Series From The DataBase #
            ##############################################################

            # Add DB Value Of Chapter
            for row in database_data:
                if row['title'] == series_title:
                    current_data = row
                    break

            db_value = current_data['last_checked_chapter']
            try:
                if str(db_value) != str(last_chapter):
                    custom_log('Not UpTo Date')

                    #############################################################################
                    # Proceed To Checking Chapter Details. Pass Last Checked Chapter Parameters #
                    #############################################################################
                    custom_log("Getting Ready To Check Chapters!")
                    check_chapters(str(last_chapter))
                else:
                    custom_log('Everything\'s Up To Date')
            except:
                custom_log('Not Checked All Chapter Details')



#############################################
#                                           #
#                                           #
#               Main Function               #
#                                           #
#                                           #
#############################################

def main():
    global driver, series_title, series_description, series_released, series_author, series_serialization, series_posted_by, series_posted_on, series_updated_on, series_artist, series_type, series_rating, series_cover_image, series_followed_by, genres, series_status, series_keywords, series_last_chapter, series_first_chapter, related_series, is_popular, is_featured, is_trending, trending_series, features, popular_all, popular_monthly, popular_weekly, popular_daily, is_popular_daily, is_popular_weekly, is_popular_monthly, is_popular_all, chapter_string
    ##############################################################
    #    Set Chrome Options And Declare the WebDriver Instance   #
    ##############################################################
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--no-sandbox')
    chrome_options.add_argument(f'--disable-gpu')
    # chrome_options.add_argument(f'--headless')
    chrome_options.binary_location = '/usr/bin/brave-browser'
    driver = uc.Chrome(options=chrome_options, headless=True)

    # driver = webdriver.Chrome(service=BraveService(CM(chrome_type=ChromeType.BRAVE).install(),), options=chrome_options)

    ##############################################################
    #  Set TimeOut Period If The Target Page Is Not Fully Loaded #
    ##############################################################
    driver.set_page_load_timeout(10)


    #####################################################################
    # Navugate To The Target Homepage. Try Used To Prevent Render Error #
    #####################################################################
    try:
        driver.get("https://www.asurascans.com/")
    except:
        custom_log('Skipping To Next Part')


    ###############################
    # Create Actiion Chain Object #
    ###############################
    actions = ActionChains(driver)

    ###################################################
    # Cycle Through Featred Comics After Page Loaded #
    ###################################################
    custom_log('AsuraScans Page Loaded. Collecting Trending!')
    try:
        trending_comics = driver.find_element(By.CLASS_NAME, 'trending')
        trending = trending_comics.find_element(By.CLASS_NAME, 'numb')
        trending_series = trending.find_element(By.TAG_NAME, 'b').text
        custom_log(trending_series)
    except:
        custom_log("Reviewing Current Page Comics!")

    custom_log('Now Collecting Featured!')
    try:
        features = ''
        featured_comics = driver.find_elements(By.CLASS_NAME, 'owl-stage')
        for comic in featured_comics:
            featured = comic.find_element(By.CLASS_NAME, 'ellipsis')
            featured_comic = featured.find_element(By.TAG_NAME, 'a').text
            features += featured_comic
            features += ','
            custom_log(features)
    except:
        custom_log("Reviewing Current Page Comics!")

    loop = 0
    popular_daily = ''

    try:
        daily_comics = driver.find_element(By.CLASS_NAME, 'hothome')
        populars_daily = daily_comics.find_elements(By.CLASS_NAME, 'tt')
        for comic in populars_daily:
            populars_daily += comic.text
    except:
        custom_log('Going To Other Populars.')


    popular_weekly = ''
    popular_monthly = ''
    popular_all = ''
    try:
        popular_comics = driver.find_elements(By.CLASS_NAME, 'leftseries')
        custom_log(len(popular_comics))
        tabs = driver.find_element(By.CLASS_NAME, 'ts-wpop-nav-tabs')
        nav = tabs.find_elements(By.TAG_NAME, 'a')
        overlay = driver.find_element(By.CLASS_NAME, 'popup_overlay--2rgA3')
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, overlay)
        for elem in nav:
            if elem.get_attribute('data-range') == 'weekly':
                elem.click()
                weekly = driver.find_element(By.CLASS_NAME, 'wpop-weekly')
                popular_comics = weekly.find_elements(By.CLASS_NAME, 'leftseries')
                for element_indiv in popular_comics:
                    loop += 1    
                    pop_series = element_indiv.find_element(By.CLASS_NAME, 'series').text
                    popular_weekly += pop_series
            elif elem.get_attribute('data-range') == 'monthly':
                elem.click()
                monthly = driver.find_element(By.CLASS_NAME, 'wpop-monthly')
                popular_comics = monthly.find_elements(By.CLASS_NAME, 'leftseries')
                for element_indiv in popular_comics:
                    loop += 1    
                    pop_series = element_indiv.find_element(By.CLASS_NAME, 'series').text
                    popular_monthly += pop_series
            elif elem.get_attribute('data-range') == 'alltime':
                elem.click()
                all_time = driver.find_element(By.CLASS_NAME, 'wpop-alltime')
                popular_comics = all_time.find_elements(By.CLASS_NAME, 'leftseries')
                for element_indiv in popular_comics:
                    loop += 1    
                    pop_series = element_indiv.find_element(By.CLASS_NAME, 'series').text
                    popular_all += pop_series

        custom_log(popular_daily)
        custom_log(popular_weekly)
        custom_log(popular_monthly)
        custom_log(popular_all)
    except Exception as e:
        custom_log(e)
        custom_log("Reviewing Current Page Comics!")


    ###################################################
    # Search & Click On Comics Link After Page Loaded #
    ###################################################
    custom_log('AsuraScans Page Loaded. Navigating To \'Comics\' Section!')
    try:
        driver.get('https://www.asurascans.com/manga/list-mode')
        custom_log('Moved To Comics Section')
    except:
        custom_log("Reviewing Current Page Comics!")



    #############################################################
    # Call Check Comics Function To Search For Available Comics #
    #############################################################
    check_comics()

main()
