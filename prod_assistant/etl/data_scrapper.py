import csv
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
sys.stdout.reconfigure(encoding='utf-8')




class FlipkartScraper:
    
    """Class for scraping product data from Flipkart."""
    
    def __init__(self, output_dir="data"):
        self.output_dir= output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        
    def  get_top_reviews(self,product_url,count=2):
        
        """Method to get top reviews for a product given its URL."""
        
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options,use_subprocess=True)

        if not product_url.startswith("http"):
            driver.quit()
            return "No reviews found"

        try:
            driver.get(product_url)
            time.sleep(4)
            try:
                close_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='✕']")))
                close_btn.click()
                time.sleep(1)
            except Exception as e:
                print(f"Error occurred while closing popup: {e}")

            for _ in range(4):
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_blocks = soup.select("div.G4PxIA")
            seen = set()
            reviews = []

            for block in review_blocks:
                text = block.get_text(separator=" ", strip=True)
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text)
                if len(reviews) >= count:
                    break
        except Exception:
            reviews = []

        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"
    
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        """Scrape Flipkart products based on a search query.
        """
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options,use_subprocess=True)
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        try:
            close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='✕']"))
            )
            close_btn.click()

        except Exception as e:
            print("Popup not found, continuing...")

        time.sleep(2)
        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
        for item in items:
            try:
                title = item.find_element(By.XPATH, ".//div[contains(@class,'RG5Slk')]").text.strip()
                
                price = item.find_element(By.XPATH, ".//div[contains(@class,'DeU9vF')]").text.strip()
                price=re.sub(r"[^\d]", "", price)
                #price="$"+price

                
                elements = item.find_elements(By.XPATH, ".//*[contains(@class,'MKiFS6')]")
                rating = elements[0].text.strip() if elements else "No rating"
                
                reviews_text = driver.find_element(By.CSS_SELECTOR, "span.PvbNMB").text.strip()
                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0).replace(",", "") if match else "N/A"


                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                time.sleep(2)
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"

            except Exception as e:
                print(f"Error occurred while processing item: {e}")
                continue

            top_reviews = self.get_top_reviews(product_link, count=review_count) if "flipkart.com" in product_link else "Invalid product URL"
            products.append([product_id, title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products
    
    def save_to_csv(self, data, filename="product_reviews.csv"):
        """Method to save scraped data to a CSV file."""
        
        if os.path.isabs(filename):
            path = filename
        elif os.path.dirname(filename):  # filename includes subfolder like 'data/product_reviews.csv'
            path = filename
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            # plain filename like 'output.csv'
            path = os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
            writer.writerows(data)
        
   
    