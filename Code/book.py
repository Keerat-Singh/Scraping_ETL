import pandas as pd
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.firefox.options import Options as Firefox_Options
import time
import sqlite3

HOMEPAGE = "http://books.toscrape.com"
# HOMEPAGE = "http://books.toscrape.com/catalogue/page-9.html"
DB_PATH = "Database/book.db"
TABLE_NAME = "Book"
# Constants for get_data_from_categories
categories = ["Humor", 'Fantasy', 'Science', 'Romance']
csv_file_name = 'books_exported.csv'
# Constants for get_data
last_page = 1   # range(1-50)
total_elements = 1000


def get_data_from_categories(url, categories):
    chrome_options = Chrome_Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    driver = Chrome(options=chrome_options)

    driver.get(url)
    driver.implicitly_wait(10)
    data = []
    for category in categories:
        humor = driver.find_element(By.PARTIAL_LINK_TEXT, category)
        humor.click()

        try:
            books = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'thumbnail'))
            )
        except Exception as e:
            raise e
        
        for book in books:
            book.click()
            time.sleep(2)

            try: 

                # Wait for the title element to be present
                title = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".col-sm-6.product_main h1"))
                )

                # Locate the div with the specific id
                description_div = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, 'product_description'))
                )

                # Now find the first <p> tag following this div
                description_paragraph = description_div.find_element(By.XPATH, 'following-sibling::p')
                keys = driver.find_elements(By.TAG_NAME, 'th')
                values = driver.find_elements(By.TAG_NAME, 'td')

                # Get the text of the paragraph
                title_text = title.text
                product_description = description_paragraph.text
                keys_text = [key.text for key in keys]
                values_text = [value.text for value in values]

                dictionary = dict(zip(keys_text, values_text))
                dictionary['Title'] = title_text
                dictionary['Description'] = product_description
                print(dictionary)

                data.append(dictionary)
                """"To store the data in a csv file later"""

                driver.back()
                time.sleep(2)
            
            except Exception as e:
                print(f"An error occurred while retrieving data: {e}")
                # Print the page source for debugging
                print(driver.page_source)

        

        driver.get(url)

    driver.quit()
    return data


def get_data(url):

    chrome_options = Chrome_Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    driver = Chrome(options=chrome_options)

    driver.get(url)
    driver.implicitly_wait(10)
    data = []
    rating_map = {
                    "Zero": 0,
                    "One": 1,
                    "Two": 2,
                    "Three": 3,
                    "Four": 4,
                    "Five": 5
                }

    cur_page = 1
    while cur_page <= last_page:
        
        try:
            books = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'thumbnail'))
            )
        except Exception as e:
            raise e
        
        for book in books:
            book.click()
            time.sleep(2)

            try: 
                # Wait for the title element to be present
                title = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".col-sm-6.product_main h1"))
                )
        
            except Exception as e:
                print(f"An error occurred while retrieving book title")
                title = None

            try: 
                # Locate the div with the specific id
                description_div = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'product_description'))
                )
                description_paragraph = description_div.find_element(By.XPATH, 'following-sibling::p')
                product_description = description_paragraph.text
            except Exception as e:
                print(f"An error occurred while retrieving book description")
                description_div = None
                product_description = None
            
            
            # Rating
            rating = driver.find_element(By.CLASS_NAME, 'star-rating')
            # print(f"Rating: {rating} \n")
            rating_text = rating.get_attribute("class").split()[-1]
            rating_text = rating_map[rating_text]

            # Now find the first <p> tag following this div
            keys = driver.find_elements(By.TAG_NAME, 'th')
            values = driver.find_elements(By.TAG_NAME, 'td')

            # Get the text of the paragraph
            title_text = title.text
            keys_text = [key.text for key in keys]
            values_text = [value.text for value in values]

            dictionary = dict(zip(keys_text, values_text))
            dictionary['Title'] = title_text
            dictionary['Description'] = product_description
            dictionary['Rating'] = rating_text
            print(dictionary)

            data.append(dictionary)
            """"To store the data in a csv file later"""

            driver.back()
            time.sleep(2)
            
                

        next = driver.find_element(By.CLASS_NAME, "next").find_element(By.TAG_NAME, "a")
        next.click()
        cur_page += 1

    driver.quit()
    return data


def export_csv(data):
    df = pd.DataFrame(data)
    # Apply transformations if needed
    df.to_csv("Code\\" + csv_file_name, index=False)
    print(df)  # DEBUG
    return df


# Function to connect to the database and create table if it doesn't exist
def connect(db_path):
    # Connect to the database (it creates the DB if it doesn't exist)
    conn = sqlite3.connect(db_path)
    # cursor = conn.cursor()
    return conn
    
def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)


def main():
    # Connect to database and create table if not exists
    # conn = connect(DB_PATH)
    # data = get_data_from_categories(url=HOMEPAGE, categories= categories)
    data = get_data(url=HOMEPAGE)
    df = export_csv(data)
    # load_to_db(df, conn, TABLE_NAME)
    # conn.close()


def run_query(query_statement, sql_connection):
    ''' This function runs the stated query on the database table and
    prints the output on the terminal. Function returns nothing. '''
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)


# For scrapping and loading the data
main()

# conn = connect(DB_PATH)
# run_query(f"SELECT * from {TABLE_NAME}", conn)
# conn.close()