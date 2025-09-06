# Dependencies

# Data Extraction and Manipulation
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException, StaleElementReferenceException, 
    TimeoutException, NoSuchElementException, ElementNotInteractableException)
import regex as re
import time
import os
import pandas as pd
import joblib as jbl
# Machine Learning
from scipy.spatial.distance import pdist, squareform
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


# ETL process for IMDb Top 250 Movies

# Extracting data from IMDb Top 250 Movies
def extract_imdb250_movies() -> pd.DataFrame:        
        '''
        Extracts IMDb Top 250 movie data from the IMDb website using Selenium. 
        The extracted data includes titles, release years, durations, ratings,
        plot descriptions, directors, lead stars, and poster URLs.
        
        Returns:
            pd.DataFrame: a Pandas DataFrame containing the data detailed above.
        '''      
        # Navigation details setup
        options_ = Options()
        options_.add_argument('--headless')    
        options_.add_argument('user-agent=MyCustomUserAgent')
        options_.add_argument('--start-maximized')
        options_.add_argument('--disable-gpu')
        options_.add_argument('--no-sandbox') 
        options_.add_argument('--disable-dev-shm-usage')
        options_.add_argument('--disable-extensions')
        options_.add_argument('--disable-popup-blocking')
        options_.add_experimental_option('excludeSwitches', ['enable-automation'])
        options_.add_experimental_option('useAutomationExtension', False)
        options_.add_argument('--disable-blink-features=AutomationControlled')
    
        # Webdriver settings
        exe = ChromeDriverManager().install()
        service = Service(exe)
        driver = webdriver.Chrome(service = service, options = options_)
        waiting = 5 # seconds
        wait_driver = WebDriverWait(driver, timeout = waiting * 4, poll_frequency = .3)
    
        # Getting to the IMDb 250 movies address page
        url = 'https://www.imdb.com/chart/top/'
        driver.get(url)
        
        # Declining cookies preferences
        try:
            cookie_preferences_decline_button = wait_driver.until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    '//*[@id="__next"]/div/div/div[2]/div/button[1]'
                    ))
                    )
            cookie_preferences_decline_button.click()
        except Exception:
            pass
        time.sleep(waiting * 2)
    
        # Fetching titles, release year, duration, and rating information
        info = [
                driver.find_element(
                    By.XPATH, 
                    f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{i+1}]'
                    ).text for i in range(250)
                ]
        titles = [re.findall(r'\d{1,3}\.\s(.*)\n', k)[0] for k in info] 
        release_year = [k.split('\n')[1] for k in info] 
        length = [k.split('\n')[2] for k in info] 
        rate = [re.findall(r'\n(\d.\d)\n', k)[0] for k in info]
    
        ### Fetching url posters 
        posters = [
            driver.find_element(
                By.XPATH,
                  f'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li[{i+1}]/div/div/div/div/div[1]/div/div[1]/img'
                  ).get_attribute('src') for i in range(250)]
        
            
        # Initial scrolling
        edge_driver.execute_script(
            'window.scrollTo(0, 410);')
    
        # Function to perform incremental scrolling (by 18% of the viewport)
        def scroll_page() -> None:
            scroll_step = edge_driver.execute_script("return window.innerHeight") * .18
            edge_driver.execute_script(f'window.scrollBy(0, {scroll_step})')
    
        # Fetching stars, descriptions, lead stars and directors data
        plots, directors, lead_stars = [], [], []
        i = 0
        while i < 250:
            
            #### Expanding movies information section (and ensuring it reads the description text) 
            open_button_path = f'''//*[@id="__next"]/main/div/div[3]/section
                                /div/div[2]/div/ul/li[{i + 1}]/div[3]/button''' 
            close_button_path = '/html/body/div[4]/div[2]/div/div[1]/button'
            description_text = ''
            description_path = '/html/body/div[4]/div[2]/div/div[2]/div/div/div[2]'
            dir_path = '/html/body/div[4]/div[2]/div/div[2]/div/div/div[3]/div[1]/ul/li/a'
            stars_path = '/html/body/div[4]/div[2]/div/div[2]/div/div/div[3]/div[2]/ul/li'
            
            while len(description_text) < 10:    
                try:  
                    # Opening the button
                    open_button = wait_driver.until(
                        EC.element_to_be_clickable((
                            By.XPATH, 
                            open_button_path
                            ))
                              )
                    open_button.click() 
    
                    # Description
                    description_section = wait_driver.until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            description_path
                            ))
                            )
                    description_text = description_section.text
                    
                    ### Getting directors information
                    dir_element = driver.find_elements(By.XPATH, 
                                                            dir_path)
                    dir_info = [dir.text for dir in dir_element]       
                    
                    # Fetcing lead stars
                    stars_info = [
                        wait_driver.until(
                            EC.visibility_of_element_located(
                                (By.XPATH, stars_path + f'[{j}]'))
                        ).text for j in range(1, 4)
                    ]
    
                    # Closing the expanded section
                    close_button = wait_driver.until(EC.element_to_be_clickable(
                        (By.XPATH, close_button_path))
                        )
                    close_button.click()
                        
                except Exception as E:        
                    if (
                            (isinstance(E, StaleElementReferenceException))
                            or 
                            (isinstance(E, TimeoutException))
                            ):
                        close_button = wait_driver.until(EC.element_to_be_clickable(
                            (By.XPATH, close_button_path))
                            )
                        close_button.click()
                        
                    elif (
                            (isinstance (E, ElementClickInterceptedException))
                            or 
                          (isinstance(E, ElementNotInteractableException))
                          ):
                        # Pushing the movie section into the center of the viewport
                        driver.execute_script(
                        '''arguments[0].scrollIntoView({'behavior': 'auto', 'block': 'center'});''',
                        open_button)
                        
                    elif isinstance(E, NoSuchElementException):
                        close_button = wait_driver.until(EC.element_to_be_clickable(
                            (By.XPATH, close_button_path)))
                        close_button.click()
                    else:
                        pass
    
            # Appending information to each respective list
            plots.append(description_text)
            directors.append(dir_info)
            lead_stars.append(stars_info)
   
            # Incremental scrolling
            scroll_page()
            i += 1 
    
        # Closing the associated browser        
        driver.quit()
            
        # Creating a dataframe with the scraped information
        imdb250_df = pd.DataFrame({'title': titles, 'plot_': plots, 
                           'release_year': release_year, 'length': length, 
                           'director_s': [' • '.join(dir_s) for dir_s in directors],
                           'lead_stars': [' • '.join(stars) for stars in lead_stars], 
                           'rate': rate, 'poster': posters
                     })
        
        return imdb250_df
              
        
# Getting similarities between IMDb Top 250 Movies 
def transform_imdb250_movies() -> pd.DataFrame:     
    '''
   Proceeds the extraction step, by using the IMDb Top 250 movies data to find
   similarities based on descriptions.

   Returns:
       pd.DataFrame: a Pandas DataFrame storing the Similarity Matrix of the 
       IMDb Top 250 movies.
   '''
    
    # Storing the IMDb data
    imdb250_df = extract_imdb250_movies()
    
    # Instantiation of TF-IDF Vectorixer
    tf_idf_vectorizer = TfidfVectorizer(min_df = .035, max_df = .8)
    vectorized_terms = tf_idf_vectorizer.fit_transform(imdb250_df.plot_)
    terms = tf_idf_vectorizer.get_feature_names_out()
    
    # Removing stopwords
    stopwords_en = stopwords.words('english')
    relevant_terms = pd.Series(terms)[~(pd.Series(terms).isin(stopwords_en))].values
    
    # Dataframe with vectorized terms for each movie
    vect_terms_df = pd.DataFrame(
        vectorized_terms.toarray(),
        columns = terms, 
        index = imdb250_df.title
                 ).loc[:, relevant_terms]
    
    # Getting the dataframe with cosine distances
    terms_matrix = (1 - squareform(
        pdist(vect_terms_df, metric = 'cosine')
        ))
    similarities_df = pd.DataFrame(terms_matrix,
                                   index = imdb250_df.title,
                                  columns = imdb250_df.title
                                  ).fillna(0).round(2)
    return similarities_df   

    
# Serializing and loading the transformed data    
def load_imdb250_movies() -> None:     
    '''
   Executes the final stage of the ETL process, by loading the data retrieved in the 
   Extraction and Transformation steps to a serialized zip instance.
   '''
   
    # Extraction and transformation
    imdb250_df = extract_imdb250_movies() 
    imdb250_similarities_df = transform_imdb250_movies()       

    # Storing the transformded data
    df_instances = ['imdb250_df', 'imdb250_similarities_df']
    zipped_data_file = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'zipped_data.joblib'))
    zipped_data_instances = zip(
        [imdb250_df, imdb250_similarities_df], df_instances
    )
    jbl.dump(zipped_data_instances, zipped_data_file)


# Triggering the ETL process execution  
load_imdb250_movies()