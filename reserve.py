#!/usr/bin/env python
from time import sleep
import os
from datetime import datetime
import time
import json
from tty import CFLAG
import click
from pprint import pprint
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

GROUPS = [
    "Mercer County Outdoor Tennis Courts S1, S2, G1, G2, 7-12", # 7:30 pm
    "Mercer County Outdoor Tennis Courts 19-24", # 6:30 PM
    "Mercer County Outdoor Tennis Courts 13-18", # 7:00 PM
]
slot_to_group = {
    (7,30): 0,
    (8,0): 1,
    (8,30): 2,
    (9,0): 0,
    (9,30): 1,
    (10,0): 2,
    (10,30): 0,
    (11,0): 1,
    (11,30): 2,
    (12,0): 0,
    (12,30): 1,
    (13,0): 2,
    (13,30): 0,
    (14,0): 1,
    (14,30): 2,
    (15,0): 0,
    (15,30): 1,
    (16,0): 2,
    (16,30): 0,
    (17,0): 1,
    (17,30): 2,
    (18,0): 0,
    (18,30): 1,
    (19,0): 2,
    (19,30): 0,
    (20,0): 1,
    (20,30): 2,
    (21,0): 0,
}
cfg = {
        **dotenv_values(".env"),
        **os.environ,
}
print( f'User={cfg["CR_USER"]}/Password={cfg["CR_PASSWORD"]}')

def get_attrs(driver, elem):
    return driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', elem)

def get_slot_info(driver, elem):
    slot = get_attrs(driver, elem)
    time_str = slot['start'][:24]
    # format looks like "Mon Jun 06 2022 22:00:00"
    start = datetime.strptime(time_str, '%a %b %d %Y %H:%M:%S')
    court = slot['courtlabel']
    return [start, court, elem]

def prettify_slot(slot):
    start = slot[0].strftime("%Y-%m-%d %H:%M")
    court = slot[1]
    return f"{start} {court}"
    court = slot[1]
    return f'{start} {court}'

def get_slots(driver):
    raw_slots = driver.find_elements(
            By.CSS_SELECTOR,
            "button.slot-btn:not(.hide)"
        )
    slots = sorted([get_slot_info(driver, slot) for slot in raw_slots])
    return slots


def get_group_slots(group):
    pass

def navigate_to_group(driver, group):
    """
    Navigate to the Court group page
    """
    reservations_menu = driver.find_element(
        By.CSS_SELECTOR, "#respMenu > .fn-ace-parent-li:nth-child(2) .arrow"
    )
    actions = ActionChains(driver)
    actions.move_to_element(reservations_menu).perform()
    # 15 | click | linkText=Mercer County Outdoor Tennis Courts 13-18 |
    driver.find_element(
        By.LINK_TEXT, group
    ).click()

def advance_day(driver, days):
    """
    Navigate to the day
    """
    next_day_btn = driver.find_element(
        By.CSS_SELECTOR,
        "button.k-nav-next"
        #"//button[contains(text(),'TODAY')]" #/following-sibling::button/following-sibling::button"
    )
    for i in range(days):
        next_day_btn.click()

def get_curr_date(driver):
    mdy = driver.find_element(
        By.CSS_SELECTOR,
        "span.k-sm-date-format"
    ).get_attribute('innerHTML')
    date = datetime.strptime(mdy, "%m/%d/%Y")
    return date

def get_group_slots(driver, group):
    navigate_to_group(driver, group)
    sleep(1)
    date = driver.find_element(
        By.CSS_SELECTOR,
        "span.k-sm-date-format"
    ).get_attribute('innerHTML')
    print(f"DBG5: {date}")
    return get_slots(driver)

def check_availability(slots, desired_time_str):
    desired_time = datetime.strptime(desired_time_str, "%Y-%m-%d_%H:%M")
    for slot in slots:
        if slot[0] == desired_time:
            return slot
    return None

def login(driver, site):
    driver.get(site)
    driver.set_window_size(1419, 1602)
    logout = driver.find_elements(By.LINK_TEXT, "Log out")
    if not logout:
        # we are NOT logged in  
        # logout[0].click()
        driver.find_element(By.LINK_TEXT, "LOG IN").click()
        user_fld = driver.find_element(By.ID, "UserNameOrEmail")
        user_fld.clear()
        user_fld.send_keys(cfg["CR_USER"])
        driver.find_element(By.ID, "Password").send_keys(cfg["CR_PASSWORD"])
        driver.find_element(By.CSS_SELECTOR, ".login_form").click()
        driver.find_element(By.CSS_SELECTOR, ".btn-log").click()    

class CourtReserve:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown(self, method):
        self.driver.quit()
    
    def navigate_to_date(self, date):
        pass

    def get_slots(self, time_slot):
        login(self.driver, cfg['CR_SITE']) # "")
        slots = []
        desired_time = datetime.strptime(time_slot, "%Y-%m-%d_%H:%M")
        hour, minute = desired_time.time().hour, desired_time.time().minute

        group = GROUPS[slot_to_group[(hour, minute)]]
        navigate_to_group(self.driver, group)

        page_date = get_curr_date(self.driver)


        while page_date.date() < desired_time.date():
            advance_day(self.driver, 1)
            page_date = get_curr_date(self.driver)
        slots += get_group_slots(self.driver, group)
        advance_day(self.driver, 1)

        return sorted(slots)

    def show_slots(self, slots):
        #slots = self.get_slots()
        pprint([prettify_slot(slot) for slot in slots])
        

    def reserve(self, slot):
        driver = self.driver
        # Click to Reserve
        slot.click()
        sleep(1)
        # Click on Save to Save Reservation
        driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Save')]"
        ).click()
        # Close the popup
        driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Close')]"
        ).click()
        sleep(1)


@click.command()
@click.option('--time_slot', help='Reserve date time. eg: 2022-06-18_19:00')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
def main(time_slot):
    cr = CourtReserve()
    slots = cr.get_slots(time_slot)
    cr.show_slots(slots)
    if time_slot:
        slot = check_availability(slots, time_slot)
        if slot:
            cr.reserve(slot[2])
        else:
            print(f"{time_slot} is not available")
        
    
if __name__ == "__main__":
    main()