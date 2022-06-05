#!/usr/bin/env python
from enum import Enum
from time import sleep
import os
from datetime import date, datetime, timedelta
import time
import json
from tty import CFLAG
from typing import Dict, List, NewType, Optional, Tuple
import click
from pprint import pprint
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

Court = NewType("Court", str)
"""A court identifying string"""

Slot = NewType("Slot", Tuple[datetime, Court, WebElement])
"""Slot is combination of a datetime and a court. This is what we reserve"""

GroupName = NewType("GroupName", str)
"""Courts are grouped by their slot time. They all have 90 minute slots. But there are three groups of courts
   with different slot times, staggered by 30 minutes.
"""

GROUPS: List[GroupName] = [
    GroupName(
        "Mercer County Outdoor Tennis Courts S1, S2, G1, G2, 7-12"
    ),  # 7:30 AM, every 90 minutes after that
    GroupName(
        "Mercer County Outdoor Tennis Courts 19-24"
    ),  # 8:00 AM, every 90 minutes after that
    GroupName(
        "Mercer County Outdoor Tennis Courts 13-18"
    ),  # 8:30 AM, every 90 minutes after that
]
#
# All possible time slots and their court group
slot_to_group: Dict[Tuple[int, int], int] = {
    (7, 30): 0,
    (8, 0): 1,
    (8, 30): 2,
    (9, 0): 0,
    (9, 30): 1,
    (10, 0): 2,
    (10, 30): 0,
    (11, 0): 1,
    (11, 30): 2,
    (12, 0): 0,
    (12, 30): 1,
    (13, 0): 2,
    (13, 30): 0,
    (14, 0): 1,
    (14, 30): 2,
    (15, 0): 0,
    (15, 30): 1,
    (16, 0): 2,
    (16, 30): 0,
    (17, 0): 1,
    (17, 30): 2,
    (18, 0): 0,
    (18, 30): 1,
    (19, 0): 2,
    (19, 30): 0,
    (20, 0): 1,
    (20, 30): 2,
    (21, 0): 0,
}

# Configuration or environment variables
cfg: Dict[str, Optional[str]] = {
    **dotenv_values(".env"),
    **os.environ,
}
# print( f'User={cfg["CR_USER"]}/Password={cfg["CR_PASSWORD"]}')


def make_driver():
    # chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    return webdriver.Chrome()


def login(driver: ChromeDriver, site: str) -> None:
    driver.get(site)
    driver.set_window_size(1419, 1602)
    sleep(3)
    logout = driver.find_elements(By.LINK_TEXT, "Log out")
    if not logout:
        print("DBG1: Logging in")
        # we are NOT logged in
        # logout[0].click()
        driver.find_element(By.LINK_TEXT, "LOG IN").click()
        user_fld = driver.find_element(By.ID, "UserNameOrEmail")
        user_fld.clear()
        user_fld.send_keys(cfg["CR_USER"])
        driver.find_element(By.ID, "Password").send_keys(cfg["CR_PASSWORD"])
        driver.find_element(By.CSS_SELECTOR, ".login_form").click()
        driver.find_element(By.CSS_SELECTOR, ".btn-log").click()


def get_elem_attrs(driver: ChromeDriver, elem: WebElement) -> Dict[str, str]:
    """
    Get the attributes of an HTML element.
    Needs Javascript code.
    """
    return driver.execute_script(
        """ var items = {};
            for (index = 0; index < arguments[0].attributes.length; ++index) {
                items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
            };
            return items;
        """,
        elem,
    )


def web_elem_to_slot(driver: ChromeDriver, elem: WebElement) -> Slot:
    slot = get_elem_attrs(driver, elem)
    time_str = slot["start"][:24]
    # format looks like "Mon Jun 06 2022 22:00:00"
    start = datetime.strptime(time_str, "%a %b %d %Y %H:%M:%S")
    court = Court(slot["courtlabel"])
    return Slot((start, court, elem))


def prettify_slot(slot: Slot) -> str:
    start = slot[0].strftime("%Y-%m-%d %H:%M")
    court = slot[1]
    return f"{start} {court}"


def get_slots_in_curr_page(driver: ChromeDriver) -> List[Slot]:
    raw_slots: List[WebElement] = driver.find_elements(
        By.CSS_SELECTOR, "button.slot-btn:not(.hide)"
    )
    slots = sorted([web_elem_to_slot(driver, slot) for slot in raw_slots])
    return slots


def navigate_to_group(driver: ChromeDriver, group: GroupName) -> None:
    """
    Navigate to the Court group page
    """
    reservations_menu: WebElement = driver.find_element(
        By.CSS_SELECTOR, "#respMenu > .fn-ace-parent-li:nth-child(2) .arrow"
    )
    actions = ActionChains(driver)
    actions.move_to_element(reservations_menu).perform()
    # 15 | click | linkText=Mercer County Outdoor Tennis Courts 13-18 |
    driver.find_element(By.LINK_TEXT, group).click()


def advance_date(driver: ChromeDriver, days: int) -> None:
    """
    Advance the date by the number of days
    """
    next_day_btn = driver.find_element(
        By.CSS_SELECTOR,
        "button.k-nav-next"
        # "//button[contains(text(),'TODAY')]" #/following-sibling::button/following-sibling::button"
    )
    for i in range(days):
        next_day_btn.click()


def get_curr_date(driver: ChromeDriver) -> datetime:
    """
    Get the date for which the current page is showing court times
    """
    mdy = driver.find_element(By.CSS_SELECTOR, "span.k-sm-date-format").get_attribute(
        "innerHTML"
    )
    date = datetime.strptime(mdy, "%m/%d/%Y")
    return date


def get_group_slots_for_day(driver: ChromeDriver, group: GroupName) -> List[Slot]:
    navigate_to_group(driver, group)
    sleep(1)

    reservations = driver.find_elements(By.CSS_SELECTOR, "div.reservation-container")
    print("Found {} reservations".format(len(reservations)))
    if reservations:
        print("Found a reservation in your name for this date")
        return []

    date = driver.find_element(By.CSS_SELECTOR, "span.k-sm-date-format").get_attribute(
        "innerHTML"
    )
    print(f"DBG5: {date}")
    return get_slots_in_curr_page(driver)


def check_availability(slots: List[Slot], desired_time_str: str) -> Optional[Slot]:
    desired_time = datetime.strptime(desired_time_str, "%Y-%m-%d_%H:%M")
    for slot in slots:
        if slot[0] == desired_time:
            return slot
    return None


def get_slots_for_datetime(driver: ChromeDriver, desired_time: datetime) -> List[Slot]:
    site = cfg["CR_SITE"]
    assert site is not None
    login(driver, site)
    hour, minute = desired_time.time().hour, desired_time.time().minute

    group = GROUPS[slot_to_group[(hour, minute)]]
    navigate_to_group(driver, group)

    page_date = get_curr_date(driver).date()

    desired_day: date = desired_time.date()
    days_to_advance = (desired_day - page_date).days
    advance_date(driver, days_to_advance)
    slots = get_group_slots_for_day(driver, group)

    return sorted(slots)


def show_slots(slots: List[Slot]) -> None:
    pprint([prettify_slot(slot) for slot in slots])


def reserve_slot(driver: ChromeDriver, slot: WebElement) -> None:
    # Click to Reserve
    slot.click()
    sleep(3)
    # Click on Save to Save Reservation
    driver.find_element(By.XPATH, "//button[contains(text(),'Save')]").click()
    sleep(3)
    # Close the popup
    driver.find_element(By.XPATH, "//button[contains(text(),'Close')]").click()
    sleep(3)


@click.command()
@click.option("--time_slot", help="Reserve date time. eg: 2022-06-18_19:00")
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
def main(time_slot):
    # Validate time slot
    assert time_slot is not None
    desired_time: datetime = datetime.strptime(time_slot, "%Y-%m-%d_%H:%M")
    desired_day: date = desired_time.date()
    assert desired_day >= date.today() and desired_day <= date.today() + timedelta(
        days=3
    ), f"{desired_day} is not in the next 3 days"

    driver: ChromeDriver = make_driver()

    slots = get_slots_for_datetime(driver, desired_time)
    show_slots(slots)
    slot = check_availability(slots, time_slot)
    if slot:
        print(f"Reserving court {prettify_slot(slot)}")
        reserve_slot(driver, slot[2])
    else:
        print(f"{time_slot} is not available")


if __name__ == "__main__":
    main()
