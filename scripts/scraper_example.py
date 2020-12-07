from selenium import webdriver
import pandas as pd

driver = webdriver.Chrome("/home/ctaranto/Projects/product_scraper/chromedriver")

driver.get('https://forums.edmunds.com/discussion/2864/general/x/entry-level-luxury-performance-sedans/p702')