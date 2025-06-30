import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from datetime import datetime
import pandas as pd

class PrizePicksScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.base_url = "https://app.prizepicks.com"
        
    def setup_driver(self, headless=True):
        """Setup undetected Chrome driver"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def scrape_sport_props(self, sport="NBA"):
        """Scrape props for specific sport"""
        print(f"🔍 Scraping {sport} props from PrizePicks...")
        
        try:
            # Navigate to PrizePicks
            self.driver.get(f"{self.base_url}/board")
            time.sleep(3)
            
            # Wait for sport selection
            sport_selector = f"//button[contains(text(), '{sport}')]"
            sport_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, sport_selector))
            )
            sport_button.click()
            time.sleep(2)
            
            # Scrape props
            props = self.extract_props()
            
            print(f"✅ Scraped {len(props)} {sport} props")
            return props
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return []
    
    def extract_props(self):
        """Extract prop data from current page"""
        props = []
        
        try:
            # Wait for props to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pick"))
            )
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find prop containers (adjust selectors based on actual PrizePicks structure)
            prop_containers = soup.find_all('div', class_='pick')
            
            for container in prop_containers:
                try:
                    prop = self.parse_prop_container(container)
                    if prop:
                        props.append(prop)
                except Exception as e:
                    print(f"⚠️ Error parsing prop: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error extracting props: {e}")
        
        return props
    
    def parse_prop_container(self, container):
        """Parse individual prop container"""
        try:
            # Extract player name (adjust selectors as needed)
            player_elem = container.find('div', class_='player-name')
            if not player_elem:
                return None
            
            player_name = player_elem.text.strip()
            
            # Extract stat type and line
            stat_elem = container.find('div', class_='stat-type')
            line_elem = container.find('div', class_='line')
            
            if not stat_elem or not line_elem:
                return None
            
            stat_type = stat_elem.text.strip()
            line_value = float(line_elem.text.strip())
            
            # Extract over/under and odds
            over_under = "over"  # PrizePicks typically shows "More than" = over
            odds = "+100"  # PrizePicks standard odds
            
            prop = {
                'player_name': player_name,
                'prop_type': stat_type.lower().replace(' ', '_'),
                'line_value': line_value,
                'bet_type': over_under,
                'odds': odds,
                'sportsbook': 'PrizePicks',
                'scraped_at': datetime.now().isoformat(),
                'sport': self.detect_sport(stat_type)
            }
            
            return prop
            
        except Exception as e:
            print(f"⚠️ Error parsing container: {e}")
            return None
    
    def detect_sport(self, stat_type):
        """Detect sport from stat type"""
        stat_lower = stat_type.lower()
        
        if any(word in stat_lower for word in ['hits', 'runs', 'rbis', 'strikeouts']):
            return 'MLB'
        elif any(word in stat_lower for word in ['yards', 'touchdowns', 'completions']):
            return 'NFL'
        elif any(word in stat_lower for word in ['points', 'rebounds', 'assists']):
            return 'NBA'
        elif any(word in stat_lower for word in ['goals', 'saves', 'assists']):
            return 'NHL'
        else:
            return 'UNKNOWN'
    
    def scrape_all_sports(self):
        """Scrape props for all available sports"""
        sports = ['NBA', 'NFL', 'MLB', 'NHL']
        all_props = []
        
        for sport in sports:
            props = self.scrape_sport_props(sport)
            all_props.extend(props)
            time.sleep(2)  # Rate limiting
        
        return all_props
    
    def save_props_to_file(self, props, filename=None):
        """Save scraped props to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prizepicks_props_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(props, f, indent=2)
        
        print(f"💾 Saved {len(props)} props to {filename}")
        return filename
    
    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    scraper = PrizePicksScraper(headless=False)  # Set True for headless
    
    try:
        # Scrape NBA props
        nba_props = scraper.scrape_sport_props("NBA")
        
        # Save to file
        if nba_props:
            scraper.save_props_to_file(nba_props)
        
    finally:
        scraper.close()