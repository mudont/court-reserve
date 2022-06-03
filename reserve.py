#!/usr/bin/env python
from time import sleep
import os
import time
import json
from pprint import pprint
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

cfg = {
        **dotenv_values(".env"),
        **os.environ,
}
print( f'User={cfg["CR_USER"]}/Password={cfg["CR_PASSWORD"]}')

def get_attrs(driver, elem):
    return driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', elem)

class Reserve:
    def __init__(self):
        print("DBG1")
        self.driver = webdriver.Chrome()
        print("DBG2")
        self.vars = {}

    def teardown(self, method):
        print("DBG teardoown")
        self.driver.quit()

    def reserve(self):
        print("DBG3")
        # Test name: Untitled
        # Step # | name | target | value
        # 1 | open | /Online/Portal/Index/7716 |
        self.driver.get("https://app.courtreserve.com/Online/Portal/Index/7716")
        # 2 | setWindowSize | 1419x1602 |
        self.driver.set_window_size(1419, 1602)
        # 3 | click | linkText=Log out |
        logout = self.driver.find_elements(By.LINK_TEXT, "Log out")
        if logout:
            logout[0].click()
        # 4 | click | linkText=LOG IN |
        self.driver.find_element(By.LINK_TEXT, "LOG IN").click()
        # 5 | type | id=UserNameOrEmail | mdonthireddy@gmail.com
        user_fld = self.driver.find_element(By.ID, "UserNameOrEmail")
        user_fld.clear()
        user_fld.send_keys(cfg["CR_USER"])
        # 6 | type | id=Password | <xxxx***xxx>
        self.driver.find_element(By.ID, "Password").send_keys(cfg["CR_PASSWORD"])
        # 7 | mouseDownAt | id=UserNameOrEmail | 188.5,20.078125
        # element = self.driver.find_element(By.ID, "UserNameOrEmail")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element).click_and_hold().perform()
        # # 8 | mouseMoveAt | id=UserNameOrEmail | 188.5,20.078125
        # element = self.driver.find_element(By.ID, "UserNameOrEmail")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element).perform()
        # # 9 | mouseUpAt | id=UserNameOrEmail | 188.5,20.078125
        # element = self.driver.find_element(By.ID, "UserNameOrEmail")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element).release().perform()
        # # 10 | click | id=UserNameOrEmail |
        # self.driver.find_element(By.ID, "UserNameOrEmail").click()
        # 11 | click | css=.login_form |
        self.driver.find_element(By.CSS_SELECTOR, ".login_form").click()
        # 12 | click | css=.btn-log |
        self.driver.find_element(By.CSS_SELECTOR, ".btn-log").click()
        #sleep(10)
        # 13 | click | css=.menu-active .arrow |
        # --> self.driver.find_element(By.CSS_SELECTOR, ".menu-active .arrow").click()
        # 14 | click | css=#respMenu > .fn-ace-parent-li:nth-child(2) .arrow |
        reservations_menu = self.driver.find_element(
            By.CSS_SELECTOR, "#respMenu > .fn-ace-parent-li:nth-child(2) .arrow"
        )
        actions = ActionChains(self.driver)
        actions.move_to_element(reservations_menu).perform()
        # 15 | click | linkText=Mercer County Outdoor Tennis Courts 13-18 |
        self.driver.find_element(
            By.LINK_TEXT, "Mercer County Outdoor Tennis Courts 13-18"
        ).click()
        print("DBG4")
        next_day_btn = self.driver.find_element(
            By.CSS_SELECTOR,
            "button.k-nav-next"
            #"//button[contains(text(),'TODAY')]" #/following-sibling::button/following-sibling::button"
        )
        date = self.driver.find_element(
            By.CSS_SELECTOR,
            "span.k-sm-date-format"
        ).get_attribute('innerHTML')
        print(f"DBG5: {date}")
        next_day_btn.click()
        print("DBG6")
        next_day_btn.click()
        next_day_btn.click()
        print("DBG7")
        slots = self.driver.find_elements(
            By.XPATH,
            "//button[contains(text(),'Reserve') and not(@class='hide')]"
        )
        #self.driver.find_element(By.CSS_SELECTOR, "
        print("DBG8")
        for slot in slots:
            attrs = get_attrs(self.driver, slot)
            pprint(attrs)
        #slot.click()
        sleep(10)
        # 16 | click | css=.k-i-arrow-60-right |
        # self.driver.find_element(By.CSS_SELECTOR, ".k-i-arrow-60-right").click()
        # # 17 | click | css=.k-i-arrow-60-right |
        # self.driver.find_element(By.CSS_SELECTOR, ".k-i-arrow-60-right").click()
        # # 18 | click |  css=.k-i-arrow-60-right |
        # self.driver.find_element(By.CSS_SELECTOR, ".k-i-arrow-60-right").click()
        # 19 | click | css=tr:nth-child(3) > .k-nonwork-hour:nth-child(2) .btn |
        # self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(3) > .k-nonwork-hour:nth-child(2) .btn").click()
        # 20 | click | css=.modal-title-buttons:nth-child(1) > .btn-primary |
        # self.driver.find_element(By.CSS_SELECTOR, ".modal-title-buttons:nth-child(1) > .btn-primary").click()
        # 21 | click | css=.btn-light |
        # self.driver.find_element(By.CSS_SELECTOR, ".btn-light").click()



Reserve().reserve()   
#print( f'user={cfg["CR_USER"]}/password={cfg["CR_PASSWORD"]}')