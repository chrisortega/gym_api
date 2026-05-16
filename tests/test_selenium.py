import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

class GymAdminSeleniumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure Chrome options
        chrome_options = Options()
        # chrome_options.add_argument("--headless") # Commented out to make tests visible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the driver
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.driver.implicitly_wait(10)
        
        # Base URL of the application
        cls.base_url = "http://localhost:3000" 

    def js_click(self, element):
        """Click an element using JavaScript to bypass overlays."""
        self.driver.execute_script("arguments[0].click();", element)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_login_page_loads(self):
        """Verify that the login page loads with the correct title."""
        self.driver.get(self.base_url)
        self.assertIn("GymAdmin", self.driver.title)
        
    def test_login_elements_present(self):
        """Check if username and password fields are present on the page."""
        self.driver.get(self.base_url)
        username_field = self.driver.find_element(By.ID, "username")
        password_field = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.ID, "submitBtn")
        
        self.assertTrue(username_field.is_displayed())
        self.assertTrue(password_field.is_displayed())
        self.assertTrue(submit_button.is_displayed())

    def test_invalid_login_error(self):
        """Check if an error message appears on failed login attempt."""
        self.driver.get(self.base_url)
        
        self.driver.find_element(By.ID, "username").send_keys("wrong_user@example.com")
        self.driver.find_element(By.ID, "password").send_keys("wrong_password")
        submit_btn = self.driver.find_element(By.ID, "submitBtn")
        self.js_click(submit_btn)
        
        time.sleep(2) # Wait for API response
        
        message_div = self.driver.find_element(By.ID, "message")
        self.assertIn("incorrectas", message_div.text.lower())

if __name__ == "__main__":
    print("Ensure the Flask app is running at http://localhost:3000 before running these tests.")
    unittest.main()
