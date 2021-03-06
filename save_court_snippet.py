# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestT2():
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_t2(self):
    self.driver.get("https://app.courtreserve.com/Online/Portal/Index/7716")
    self.driver.set_window_size(1419, 1602)
    self.driver.find_element(By.LINK_TEXT, "LOG IN").click()
    self.driver.find_element(By.ID, "UserNameOrEmail").send_keys("mdonthireddy@gmail.com")
    self.driver.find_element(By.ID, "Password").send_keys("Anbarivu1")
    self.driver.find_element(By.CSS_SELECTOR, ".btn-log").click()
    self.driver.find_element(By.CSS_SELECTOR, ".menu-active .title").click()
    self.driver.find_element(By.CSS_SELECTOR, "#respMenu > .fn-ace-parent-li:nth-child(2) .title").click()
    self.driver.find_element(By.LINK_TEXT, "Mercer County Outdoor Tennis Courts 13-18").click()
    self.driver.find_element(By.CSS_SELECTOR, ".reservation-container").click()
    self.driver.find_element(By.CSS_SELECTOR, ".btn-transparent").click()
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    self.driver.close()
    self.driver.find_element(By.LINK_TEXT, "Mercer County Outdoor Tennis Courts 19-24").click()
    self.driver.find_element(By.CSS_SELECTOR, ".k-i-arrow-60-right").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(4) > .k-nonwork-hour:nth-child(2) .btn").click()
    self.driver.find_element(By.CSS_SELECTOR, ".modal-title-buttons:nth-child(1) > .btn-primary").click()
    self.driver.find_element(By.CSS_SELECTOR, ".btn-light").click()
  
