import pandas as pd
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import sqlite3
import random
import numpy
import os

# Initialize WebDriver with custom headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'accept' : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    'accept_language' : "en-US,en;q=0.5",
    'connection' : "keep-alive",
    'upgrade_insecure_requests' : "1",
    'cache_control' : "max-age=0",
    'referer' : "https://www.google.com/",
    'accept_encoding' : "gzip, deflate, br"
}
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
CHROME_DRIVER_PATH = 'c:/WebDrivers/chromedriver.exe'
HOMEPAGE = "https://www.realtor.ca/on/toronto/real-estate"
HOMEPAGE = "https://www.realtor.ca/real-estate/27603470/867-windermere-avenue-toronto-runnymede-bloor-west-village-runnymede-bloor-west-village"
DB_PATH = "Database/Real_estate.db"
TABLE_NAME = "RealEstate"
last_page = 5
total_elements = 1000


def randomizer(driver, mouse_movement_timer: int= 3, scroll_timer: int = 3):
    """To make random mouse movement or sleep to make it more natural that its a person using"""
    random_mouse_movement(driver, duration= mouse_movement_timer)
    random_scroll(driver, scroll_time= scroll_timer)

def captcha_handler(driver):
    """"To handle captcha"""
    try:

        captcha = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "geetest_holder"))
            )
        # captcha = driver.find_element(By.CLASS_NAME, 'captcha')
        # randomizer(driver)
        captcha.find_element(By.CLASS_NAME, 'geetest_btn').click()
        print("working on handling captcha")


        # geetest_widget --wait until this is done

        # geetest_voice --wait until this is done

        # geetest_voice_wrap -- wait until this shows up from the above

        # geetest_replay -- click this to start the voice captcha

        # use gpt to decode the message and convert the number 

        # geetest_input --  feed that number here

        # geetest_submit -- once entered submit the number
    
    except Exception as e:
        print(f"An error occured during solving captcha: {e}")
        input("Testing")
        # driver.quit()


def get_data(url):
    """Scraping data for the initial url provided"""
    chrome_options = Chrome_Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    driver = Chrome(options= chrome_options)

    driver.get(url)
    driver.execute_script("""
        var req = new XMLHttpRequest();
        req.open('GET', window.location.href, true);
        req.setRequestHeader('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8');
        req.setRequestHeader('Accept-Language', 'en-US,en;q=0.5');
        req.setRequestHeader('Connection', 'keep-alive');
        req.setRequestHeader('Upgrade-Insecure-Requests', '1');
        req.setRequestHeader('Cache-Control', 'max-age=0');
        req.send();
    """)

    driver.implicitly_wait(10)
    data = []

    cur_page = 1
    while cur_page < last_page:
        
        try:
            listings = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'cardCon'))
            )
        except Exception as e:
            raise e
        
        for listing in listings:
            listing.click()     # TODO this opens the link in the new page
            time.sleep(2)       # Randomize?

            """Will be used to create a dictionary to be saved to be to save a csv file"""
            key = []
            value = []

            try: 

                # Wait for the title element to be present
                TopCon = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "listingDetailsTopCon"))
                )

                listingPrice = TopCon.find_element(By.ID, 'listingPrice').text
                print(f"Listing Price: {listingPrice}")
                listingAddress = TopCon.find_element(By.ID, 'listingAddress').text
                print(f"Listing Address: {listingAddress}")
                mlNumberVal = TopCon.find_element(By.ID, 'MLNumberVal').text
                print(f"ML Number: {mlNumberVal}")


                InfoTab = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, 'listingInfoTab'))
                )

                propertyDescription = InfoTab.find_element(By.ID, 'propertyDescriptionCon').text
                print(f"ML Number: {propertyDescription}")
                propertyDetailsSectionContentSubCon = InfoTab.find_elements(By.CLASS_NAME, 'propertyDetailsSectionContentSubCon')
                for i in propertyDetailsSectionContentSubCon:
                    key.append(i.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentLabel').text)
                    value.append(i.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentValue').text)
                print(f'Value of key: {key}')
                print(f'Value of value: {value}')


                ListingDetailsBuildingCon = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "listingDetailsBuildingCon"))
                )
                propertyDetailsValueSubSectionCon = ListingDetailsBuildingCon.find_elements(By.CLASS_NAME, 'propertyDetailsValueSubSectionCon')
                for i in propertyDetailsValueSubSectionCon:
                    # This is the header which will be used to make key name
                    header = i.find_element(By.CLASS_NAME, 'propertyDetailsValueSubSectionHeader').text
                    SubCon = i.find_elements(By.CLASS_NAME, 'propertyDetailsSectionContentSubCon')
                    for j in SubCon:
                        key_text = header + '_' + j.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentLabel').text
                        value_text = header + '_' + j.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentValue').text
                        key.append(key_text)
                        value.append(value_text)

                print("\n")
                print(f'Value of key: {key}')
                print(f'Value of value: {value}')


                input("Wait")


                # # Now find the first <p> tag following this div
                # description_paragraph = description_div.find_element(By.XPATH, 'following-sibling::p')
                # keys = driver.find_elements(By.TAG_NAME, 'th')
                # values = driver.find_elements(By.TAG_NAME, 'td')

                # # Get the text of the paragraph
                # title_text = title.text
                # product_description = description_paragraph.text
                # keys_text = [key.text for key in keys]
                # values_text = [value.text for value in values]

                # dictionary = dict(zip(keys_text, values_text))
                # dictionary['Title'] = title_text
                # dictionary['Description'] = product_description
                # print(dictionary)

                # data.append(dictionary)
                # """"To store the data in a csv file later"""

                # driver.back()
                # time.sleep(2)
            
            except Exception as e:
                print(f"An error occurred while retrieving data: {e}")
                # Print the page source for debugging
                print(driver.page_source)

        next = driver.find_elements(By.CLASS_NAME, "paginationLinkText")[-2]
        next.click()
        cur_page += 1

    driver.quit()
    return data


def specific_page(url):
    """To test if the scraping of the page is working as intended"""
    chrome_options = Chrome_Options()
    chrome_options.add_argument(f"--user-agent= {USER_AGENT}")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    driver = Chrome(options= chrome_options)
    # driver.maximize_window()
    # driver.execute_script("""
    #     var req = new XMLHttpRequest();
    #     req.open('GET', window.location.href, true);
    #     req.setRequestHeader('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8');
    #     req.setRequestHeader('Accept-Language', 'en-US,en;q=0.5');
    #     req.setRequestHeader('Connection', 'keep-alive');
    #     req.setRequestHeader('Upgrade-Insecure-Requests', '1');
    #     req.setRequestHeader('Cache-Control', 'max-age=0');
    #     req.send();
    # """)

    driver.get(url)
    driver.implicitly_wait(10)
    # randomizer(driver)
    data = []


    key = []
    value = []

    try: 

        # Wait for the title element to be present
        TopCon = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "listingDetailsTopCon"))
        )
        listingPrice = TopCon.find_element(By.ID, 'listingPrice').text
        key.append('Listing Price')
        value.append(listingPrice)
        print(f"Listing Price: {listingPrice}")
        listingAddress = TopCon.find_element(By.ID, 'listingAddress').text
        key.append('Listing Address')
        value.append(listingAddress)
        print(f"Listing Address: {listingAddress}")
        mlNumberVal = TopCon.find_element(By.ID, 'MLNumberVal').text
        key.append('ML Number')
        value.append(mlNumberVal)
        print(f"ML Number: {mlNumberVal}")

        # Maybe do some random movement --here
        InfoTab = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'listingInfoTab'))
        )

        propertyDescription = InfoTab.find_element(By.ID, 'propertyDescriptionCon').text
        print(f"Discription: {propertyDescription}")
        propertyDetailsSectionContentSubCon = InfoTab.find_elements(By.CLASS_NAME, 'propertyDetailsSectionContentSubCon')
        for i in propertyDetailsSectionContentSubCon:
            key.append(i.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentLabel').text)
            value.append(i.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentValue').text)
        print(f'Value of key: {key}')
        print(f'Value of value: {value}')


        ListingDetailsBuildingCon = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "listingDetailsBuildingCon"))
        )
        propertyDetailsValueSubSectionCon = ListingDetailsBuildingCon.find_elements(By.CLASS_NAME, 'propertyDetailsValueSubSectionCon')
        for i in propertyDetailsValueSubSectionCon:
            # This is the header which will be used to make key name
            header = i.find_element(By.CLASS_NAME, 'propertyDetailsValueSubSectionHeader').text
            SubCon = i.find_elements(By.CLASS_NAME, 'propertyDetailsSectionContentSubCon')
            for j in SubCon:
                key_text = header + '_' + j.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentLabel').text
                value_text = header + '_' + j.find_element(By.CLASS_NAME, 'propertyDetailsSectionContentValue').text
                key.append(key_text)
                value.append(value_text)

        print("\n")
        print(f'Value of key: {key}')
        print(f'Value of value: {value}')

        driver.close()

        # Converting the key and value pair to a dict which is to be saved in a csv file
        data.append(dict(zip(key, value)))

    except Exception as e:
        print(f"An error occurred while retrieving data: {e}")
        # print(driver)
        # print("Going to cache to solve it")
        # Print the page source for debugging
        captcha_handler(driver)
        

       
    # input("Wait")
    driver.quit()
    return data


def bezier_curve(start, end, t):
    """Calculate a point on a Bézier curve."""
    # Quadratic Bezier curve: P(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
    # Here we assume P0 is start, P1 is midpoint, P2 is end
    # For simplicity, we use a straight line for P1
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + random.randint(-50, 50))  # Offset for curve
    return (
        (1-t)**2 * start[0] + 2 * (1-t) * t * midpoint[0] + t**2 * end[0],
        (1-t)**2 * start[1] + 2 * (1-t) * t * midpoint[1] + t**2 * end[1]
    )

def random_mouse_movement(driver, duration=5):
    """Move the mouse randomly on the page for a specified duration with curved movements."""
    end_time = time.time() + duration  # Run for 'duration' seconds
    action = ActionChains(driver)

    # Initial position (start)
    current_pos = (random.randint(0, driver.get_window_size()['width']),
                   random.randint(0, driver.get_window_size()['height']))

    while time.time() < end_time:
        # Get window size and generate random target position
        window_size = driver.get_window_size()
        target_pos = (random.randint(0, window_size['width']),
                      random.randint(0, window_size['height']))

        # Move in a curved path from current position to target position
        steps = 30  # Number of steps in the curve
        for step in range(steps + 1):
            t = step / steps  # Normalize to [0, 1]
            curve_point = bezier_curve(current_pos, target_pos, t)

            # Move to the calculated point
            action.move_by_offset(curve_point[0] - current_pos[0], curve_point[1] - current_pos[1]).perform()
            current_pos = curve_point  # Update current position

            # Sleep for a short duration before the next step
            time.sleep(0.05)  # Adjust for smoothness

        # Sleep for a random duration before moving again
        time.sleep(random.uniform(0.5, 2))

def random_scroll(driver, scroll_time=5):
    """Scroll randomly on the page for a specified duration."""
    end_time = time.time() + scroll_time  # Run for 'scroll_time' seconds

    while time.time() < end_time:
        # Randomly choose to scroll up or down
        scroll_direction = random.choice([-1, 1])  # -1 for up, 1 for down
        scroll_amount = random.randint(200, 600)  # Random scroll amount
        
        # Execute JavaScript to scroll the page
        driver.execute_script(f"window.scrollBy(0, {scroll_direction * scroll_amount});")
        
        # Sleep for a short duration before the next scroll
        time.sleep(random.uniform(0.5, 2))  # Random wait between 0.5 to 2 seconds


def export_csv(data):
    df = pd.DataFrame(data)
    # Check if the file already exists
    file_path = "CSV/rental_listing.csv"
    if os.path.exists(file_path):
        # Load the existing data
        existing_df = pd.read_csv(file_path)
        # Append the new data to the existing data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
    else:
        # If the file doesn't exist, just use the new data
        combined_df = df
    
    # Remove duplicate entries
    combined_df.drop_duplicates(inplace= True)
    print(f"After remooval?: {combined_df}")
    # Save the combined data to the CSV file
    combined_df.to_csv(file_path, index=False)
    print(combined_df)  # DEBUG
    return combined_df


# Function to connect to the database
def connect(db_path):
    # Connect to the database (it creates the DB if it doesn't exist)
    conn = sqlite3.connect(db_path)
    return conn

def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)


def main():
    # Connect to database and create table if not exists
    conn = connect(DB_PATH)
    # data = get_data(url=HOMEPAGE)
    data = specific_page(url=HOMEPAGE)
    df = export_csv(data)
    load_to_db(df, conn, TABLE_NAME)
    conn.close()
    # First set header info

    # URL and other details

    """Begin scrapping -- using webdriverwait need to check for captcha, get page info when fails to load the specific page; 
    timer could be randomized"""

    # Can get chatgpt or other text tool to bypass captcha



main()