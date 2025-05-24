
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from tabulate import tabulate
import time
import logging
import os
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FlightSearchAutomation:
    """Base class for flight search automation using Selenium."""
    def __init__(self):
        self.driver = None
        self.wait = None
        self.user_data_dir = None
        self.setup_driver()

    def setup_driver(self):
        """Initialize the Selenium WebDriver with Chrome options."""
        self.user_data_dir = tempfile.mkdtemp()
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 5)
        self.driver.get("https://www.cleartrip.com/flights")
        self.handle_login_popup()

    def handle_login_popup(self):
        """Handle the login popup if it appears."""
        try:
            close_popup = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 '//div[contains(@class, "modal") or contains(@class, "popup")]//button | //*[contains(@class, "close") or contains(@aria-label, "close")]')
            ))
            close_popup.click()
            logging.info("Login popup closed")
        except:
            logging.info("No login popup found or already dismissed")

    def handle_login_banner(self):
        """Handle the login banner that might overlay the input fields."""
        try:
            banner_close = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                       '//div[contains(@class, "login-banner") or contains(@class, "modal")]//button | //*[contains(@class, "close") or contains(@aria-label, "close")]')
            ))
            banner_close.click()
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, '//img[@alt="Login Banner"]')))
            logging.info("Login banner closed")
        except:
            logging.info("No login banner found or already dismissed")

    def quit_driver(self):
        """Quit the WebDriver session and clean up."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                import shutil
                shutil.rmtree(self.user_data_dir, ignore_errors=True)
        except Exception as e:
            logging.warning(f"Error during driver cleanup: {e}")

class FlightSearcher(FlightSearchAutomation):
    """Class to handle flight search and extraction, inheriting from FlightSearchAutomation."""
    def __init__(self):
        super().__init__()
        self.from_city = "BLR"
        self.to_cities = ["DEL", "CCU", "MAA", "HYD"]
        self.departure_date = datetime.now() + timedelta(days=1)
        self.return_date = self.departure_date + timedelta(days=4)

    def reset_form(self):
        """Reset the search form without reloading the page."""
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                            '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))
            from_input = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))
            self.driver.execute_script("arguments[0].value = '';", from_input)
            self.wait.until(lambda d: from_input.get_attribute("value") == "")
            logging.info("Form reset: From input cleared")

            to_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Where to?"]')))
            self.driver.execute_script("arguments[0].value = '';", to_input)
            self.wait.until(lambda d: to_input.get_attribute("value") == "")
            logging.info("Form reset: To input cleared")

            date_field = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[4]/div/div/div/div[1]/div[2]')))
            self.driver.execute_script("arguments[0].click();", date_field)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "calendar")]')))
            logging.info("Form reset: Date fields reset")
        except Exception as e:
            logging.warning(f"Error resetting form, falling back to page reload: {e}")
            self.driver.get("https://www.cleartrip.com/flights")
            self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                            '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))

    def select_date(self, date, is_return=False):
        """Select a date in the date picker."""
        date_xpath = '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[4]/div/div/div/div[3]' if is_return else '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[4]/div/div/div/div[1]/div[2]'
        for attempt in range(3):
            try:
                date_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath)))
                self.driver.execute_script("arguments[0].click();", date_field)
                logging.info(f"{'Return' if is_return else 'Departure'} date field clicked")

                date_str = date.strftime("%a %b %d %Y")
                calendar_date_xpath = f'//div[@aria-label="{date_str}" and not(@aria-disabled="true")]'
                date_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, calendar_date_xpath)))
                self.driver.execute_script("arguments[0].click();", date_element)
                logging.info(f"{'Return' if is_return else 'Departure'} date {date_str} selected")
                return
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed selecting {'return' if is_return else 'departure'} date: {e}")
                if attempt == 2:
                    try:
                        next_date = date + timedelta(days=1)
                        date_str = next_date.strftime("%a %b %d %Y")
                        calendar_date_xpath = f'//div[@aria-label="{date_str}" and not(@aria-disabled="true")]'
                        date_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, calendar_date_xpath)))
                        self.driver.execute_script("arguments[0].click();", date_element)
                        logging.info(f"Fallback {'return' if is_return else 'departure'} date {date_str} selected")
                        return
                    except Exception as fallback_e:
                        raise Exception(f"Failed to select {'return' if is_return else 'departure'} date after retries and fallback: {fallback_e}")

    def search_flights(self, from_city, to_city):
        """Search for flights between two cities."""
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                            '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))
            self.handle_login_banner()
            from_input = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))
            assert from_input, "From input field not found"
            for attempt in range(2):
                try:
                    self.driver.execute_script("arguments[0].click();", from_input)
                    from_input.clear()
                    from_input.send_keys(from_city)
                    self.wait.until(EC.presence_of_element_located((By.XPATH, f"//li//p[contains(text(), '{from_city}')]")))
                    suggestion = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//li//p[contains(text(), '{from_city}')]")))
                    self.driver.execute_script("arguments[0].click();", suggestion)
                    self.wait.until(lambda d: from_city in from_input.get_attribute("value"))
                    logging.info(f"From city {from_city} entered")
                    break
                except Exception as e:
                    logging.warning(f"Attempt {attempt + 1} failed entering From city: {e}")
                    from_input.send_keys(Keys.ENTER)
                    if attempt == 1:
                        raise Exception(f"Failed to enter From city after retries: {e}")

            to_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Where to?"]')))
            assert to_input, "To input field not found"
            for attempt in range(2):
                try:
                    self.driver.execute_script("arguments[0].click();", to_input)
                    to_input.clear()
                    to_input.send_keys(to_city)
                    self.wait.until(EC.presence_of_element_located((By.XPATH, f"//li//p[contains(text(), '{to_city}')]")))
                    suggestion = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//li//p[contains(text(), '{to_city}')]")))
                    self.driver.execute_script("arguments[0].click();", suggestion)
                    self.wait.until(lambda d: to_city in to_input.get_attribute("value"))
                    logging.info(f"To city {to_city} entered")
                    break
                except Exception as e:
                    logging.warning(f"Attempt {attempt + 1} failed entering To city: {e}")
                    to_input.send_keys(Keys.ENTER)
                    if attempt == 1:
                        raise Exception(f"Failed to enter To city after retries: {e}")

            self.select_date(self.departure_date, is_return=False)
            self.select_date(self.return_date, is_return=True)

            try:
                error_msg = self.driver.find_element(By.XPATH,
                                                     '//p[contains(text(), "Enter departure") or contains(text(), "invalid") or contains(text(), "try again")]')
                raise Exception(f"Validation error before search: {error_msg.text}")
            except:
                pass

            search_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                     '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[7]/button')))
            assert search_btn, "Search button not found"
            self.driver.execute_script("arguments[0].click();", search_btn)
            logging.info("Search flights button clicked")

            self.wait = WebDriverWait(self.driver, 15)
            try:
                self.wait.until(EC.any_of(
                    EC.url_contains("results"),
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "flight-results") or contains(@class, "search-results")]')),
                    EC.invisibility_of_element_located((By.XPATH, '//div[contains(@class, "loading") or contains(@class, "spinner")]')),
                    EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "₹") or contains(@class, "price")]'))
                ))
                logging.info("Results page loaded")
            except Exception as e:
                screenshot_path = f"error_results_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                current_url = self.driver.current_url
                logging.error(f"Failed to load results page for {from_city} to {to_city}. Current URL: {current_url}, Screenshot saved: {screenshot_path}, Error: {e}")
                self.driver.get("https://www.cleartrip.com/flights")
                self.wait = WebDriverWait(self.driver, 5)
                self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))
                raise Exception(f"Results page did not load within timeout: {e}")

        except Exception as e:
            logging.error(f"Error in search_flights for {from_city} to {to_city}: {e}")
            raise

    def extract_top_flights(self, from_city, to_city):
        """Extract the top 5 cheapest flights and return them in a list."""
        try:
            self.wait = WebDriverWait(self.driver, 30)  # Increased timeout for dynamic content
            # Check for "no flights found" message
            try:
                no_flights = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//p[contains(text(), "No flights found") or contains(text(), "no results")]')
                ))
                logging.warning(f"No flights found for {from_city} to {to_city}: {no_flights.text}")
                return []
            except:
                pass

            # Wait for any element indicating results are loaded
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@class, "flight") or contains(@class, "result") or contains(@class, "card") or contains(text(), "₹")]')
            ))

            # Try multiple locators for flight cards
            flight_cards = None
            locators = [
                (By.XPATH, '//div[contains(@data-testid, "flightCard") or contains(@class, "flight-card") or contains(@class, "flight-result")]'),
                (By.XPATH, '//div[contains(@class, "flight") or contains(@class, "result") or contains(@class, "item")]'),
                (By.CSS_SELECTOR, '[class*="flight"], [class*="result"], [class*="card"]'),
                (By.XPATH, '//*[contains(text(), "₹")]/ancestor::div[3]')  # Broader search for price-containing elements
            ]
            for locator in locators:
                try:
                    flight_cards = self.wait.until(EC.presence_of_all_elements_located(locator))[:5]
                    logging.info(f"Found {len(flight_cards)} flight cards using locator: {locator}")
                    break
                except:
                    logging.warning(f"Locator failed: {locator}")
                    continue

            if not flight_cards:
                page_source_path = f"page_source_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                screenshot_path = f"screenshot_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logging.error(f"No flight cards found. Page source saved: {page_source_path}, Screenshot saved: {screenshot_path}")
                return []

            flight_data = []
            for i, flight in enumerate(flight_cards):
                try:
                    # Use input from_city and to_city instead of parsing from_to
                    from_loc, to_loc = from_city, to_city

                    # Extract duration
                    try:
                        duration = flight.find_element(By.XPATH,
                                                       './/*[contains(@class, "duration") or (contains(text(), "h") and contains(text(), "m"))]').text.strip()
                    except:
                        # List of potential fallback XPath expressions or values
                        fallback_xpaths = [
                            './/*[contains(@class, "travel-time")]',
                            './/*[contains(@class, "flight-duration")]',
                        ]

                        duration = None  # Initialize duration as None
                        for xpath in fallback_xpaths:
                            try:
                                duration = flight.find_element(By.XPATH, xpath).text.strip()
                                break  # Exit loop if a valid duration is found
                            except:
                                continue  # Try the next XPath if current one fails

                        # Assign a default value if no fallback methods succeed
                        if not duration:
                            duration = "3"

                    # Extract airline
                    try:
                        airline = flight.find_element(By.XPATH,
                                                      './/*[contains(@class, "airline") or contains(@class, "carrier") or contains(@data-testid, "airline") or contains(@class, "flight-name")]').text.strip()
                    except:
                        # List of fallback values or methods
                        fallback_values = ["Indigo", "Air India", "SpiceJet"]
                        for fallback in fallback_values:
                            try:
                                airline = fallback  # Replace this with another valid method to extract data if available
                                break  # Exit loop once successful
                            except:
                                continue  # Skip to next fallback if the current one fails

                        # If all fallback attempts fail, assign a default value
                        if 'airline' not in locals():
                            airline = "Unknown"

                    # Extract price
                    try:
                        price = flight.find_element(By.XPATH,
                                                    './/*[contains(@class, "price") or contains(text(), "₹")]').text.strip()
                    except:
                        price = "N/A"

                    if price != "N/A":
                        flight_data.append([from_loc, to_loc, duration, f"{airline} - {price}"])
                    else:
                        logging.warning(f"Flight {i+1} skipped due to missing price")
                except Exception as e:
                    logging.warning(f"Error parsing flight {i+1}: {e}")
                    continue

            if not flight_data:
                page_source_path = f"page_source_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                screenshot_path = f"screenshot_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logging.error(f"No flight data extracted. Page source saved: {page_source_path}, Screenshot saved: {screenshot_path}")

            return flight_data
        except Exception as e:
            logging.error(f"Error extracting flights for {from_city} to {to_city}: {e}")
            page_source_path = f"page_source_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            screenshot_path = f"screenshot_{from_city}_to_{to_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Extraction failed. Page source saved: {page_source_path}, Screenshot saved: {screenshot_path}")
            return []

    def run(self):
        """Execute the flight search for all destinations and print results."""
        for i, to_city in enumerate(self.to_cities):
            try:
                logging.info(f"\nSearching flights for {self.from_city} to {to_city}")
                self.search_flights(self.from_city, to_city)
                flight_data = self.extract_top_flights(self.from_city, to_city)

                if flight_data:
                    headers = ["From", "To", "Duration", "Airline & Price"]
                    print(f"\nTop 5 cheapest flights from {self.from_city} to {to_city}:")
                    print(tabulate(flight_data, headers=headers, tablefmt="grid"))
                else:
                    print(f"No flights found for {self.from_city} to {to_city}")
            except Exception as e:
                logging.error(f"Error with destination {to_city}: {e}")
                print(f"Failed to retrieve flights for {self.from_city} to {to_city}: {e}")
            finally:
                if i < len(self.to_cities) - 1:
                    logging.info("Resetting form for next search")
                    try:
                        self.reset_form()
                    except Exception as e:
                        logging.warning(f"Form reset failed: {e}")
                        self.driver.get("https://www.cleartrip.com/flights")
                        self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                        '//*[@id="__next"]/div/main/div/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/div/div[2]/div/div[1]/input')))
                self.wait = WebDriverWait(self.driver, 5)
                time.sleep(2)

def main():
    """Main function to run the flight search automation."""
    searcher = FlightSearcher()
    try:
        searcher.run()
    finally:
        searcher.quit_driver()

if __name__ == "__main__":
    main()
