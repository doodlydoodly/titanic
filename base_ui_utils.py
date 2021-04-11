#!/usr/bin/env python
#

from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from lib.log import Log
from lib.pca.pca_3x.constants.test_resources import PCA3_TENANT_NAME
from lib.pca.pca_3x.constants.ui_constants.IAM.Users.user_home_constants import NAMES_LIST_XPATH, \
    NEXT_PAGE_BUTTONS_XPATH, OCID_OF_LIST_ITEM_XPATH, LIST_OF_ITEMS_ON_PAGE_XPATH, STATE_XPATH
from lib.pca.pca_3x.constants.ui_constants.Networking.drg_home_constants import DRG_DETAILS_COMPARTMENT_DROPDOWN, \
    DRG_DETAILS_COMPARTMENT_SELECTION_LIST_XPATH, DRG_DETAILS_COMPARTMENT_SELECTION_XPATH, COMPARTMENT_RELOAD_BUTTON, \
    DRG_ALREADY_SELECTED_COMPARTMENT_XPATH
from lib.pca.pca_3x.constants.ui_constants.Networking.vcn_create_constants import LIST_FILTER_TAG_XPATH, \
    VCN_LIST_DEFINED_TAGS_TAB_XPATH, VCN_LIST_FREEFORM_TAGS_TAB_XPATH, VCN_LIST_FILTER_TAG_BUTTON_XPATH, \
    VCN_CREATE_DNS_HOSTNAMES_CHECKBOX_XPATH
from lib.pca.pca_3x.constants.ui_constants.driver_constants import OSSE_CHROMEDRIVER_WINDOWS_PATH, \
    OSSE_CHROMEDRIVER_LINUX_PATH
from lib.pca.pca_3x.constants.ui_constants.ui_constants import CONTAINS_TEXT_HEADER
from lib.pca.pca_3x.utils.CE.IAM.compartment_utils.compartment_rest import CompartmentRestUtils
from tests.pca_3x.config import OSSE_UI_OPERATING_SYSTEM


def clear_field_by_class_name(driver, class_name):
    """
    clear_field_by_class_name

    Searches for a text field by class name and clears it

    :param driver: Webdriver controller for the web page
    :param class_name: Name of the class to find and clear
    """
    Log.info(f"Clearing field with class name {class_name}")
    element = driver.find_element_by_class_name(class_name)
    element.clear()

def clear_field_by_id(driver, element_id):
    """
    clear_field_by_xpath

    Searches for a text field by ID and clears it

    :param driver: Webdriver controller for the web page
    :param element_id: ID of the field to find and clear
    """
    Log.info(f"Clearing field with element ID {element_id}")
    element = driver.find_element_by_id(element_id)
    element.clear()

def clear_field_by_xpath(driver, xpath):
    """
    clear_field_by_xpath

    Searches for a text field by xpath and clears it

    :param driver: Webdriver controller for the web page
    :param xpath: Xpath of the field to find and clear
    """
    Log.info(f"Clearing field with XPath name {xpath}")
    element = driver.find_element_by_class_name(xpath)
    element.clear()

def click_by_class(driver, class_name):
    """
    click_by_class

    Clicks an element found by using class

    :param driver: Webdriver controller for the web page
    :param class_name: Name of the class to click
    """
    Log.info(f"Clicking element with class {class_name}")
    element = driver.find_element_by_class_name(class_name)
    element.click()

def click_element_by_id(driver, element_id):
    """
    click_element_by_xpath

    Generates a contains string for searching for an element on a page

    :param driver: Webdriver controller for the web page
    :param element_id: ID of the element to click
    """
    Log.info(f"Clicking element with ID {element_id}")
    element = driver.find_element_by_id(element_id)
    element.click()

def click_element_by_xpath(driver, xpath):
    """
    click_element_by_xpath

    Clicks an element by its xpath

    :param driver: Webdriver controller for the web page
    :param xpath: Xpath of the element to click
    """
    Log.info(f"Clicking element with Xpath {xpath}")
    element = driver.find_element_by_xpath(xpath)
    element.click()


def click_then_wait_for_element_not_to_be_present(driver, element_xpath_or_id, element_type='xpath', wait_interval=5,
                                                  max_wait_time=60):
    """

    click_then_wait_for_element_not_to_be_present

    Clicks an element, then recursively checks for the element to not be clickable. Useful where e.g Clicking a dialog
    "submit" button and wishing to return to the details page. So the submit button should be gone after we click it.

    :param driver: Webdriver for the browser
    :param element_xpath_or_id: Xpath or ID of the element we want to not be clickable. Based on element_type
    :param element_type: Xpath or ID
    :param wait_interval: Sleep interval between checks
    :param max_wait_time: Timeout for the element to not be clickable
    :return:
    """
    if element_type == 'xpath':
        click_element_by_xpath(driver, element_xpath_or_id)
    else:
        click_element_by_id(driver, element_xpath_or_id)
    wait_for_element_not_to_be_clickable(driver, element_xpath_or_id, element_type, wait_interval, max_wait_time)

def find_and_click_checkbox_from_display_name(driver, name_to_search_for, names_list_xpath, checkbox_list_xpath):
    """
    find_and_click_checkbox_from_display_name

    Utility to find the row of a checkbox and click it based on it's resource name adjacent

    :param driver: Webdriver for the browser
    :param name_to_search_for: Text of the adjacent item to the checkbox
    :param names_list_xpath: Xpath to the list of resource name elements
    :param checkbox_list_xpath:  Xpath to the list of resource checkbox elements
    """
    name_checkboxes = driver.find_elements_by_xpath(checkbox_list_xpath)
    display_names = driver.find_elements_by_xpath(names_list_xpath)
    index = 0
    list_checked = []
    for display_name in display_names:
        display_name = display_name.text
        list_checked.append(display_name)
        Log.info(f"Checking whether {display_name} matches the desired string {name_to_search_for}")
        if name_to_search_for == display_name:
            element = name_checkboxes[index]
            Log.info(f"Found the desired string. Clicking the adjacent checkbox at index {index}.")
            element.click()
            driver.save_screenshot("this.png")
            return
        index += 1
    raise FileNotFoundError(f"Did not find element to click. Elements available were {list_checked[0:-1]}")

def find_by_id(driver, element_id):
    """
    find_by_id

    Finds using element ID, an element on a page

    :param driver: Webdriver controller for the web page
    :param element_id: ID of the element

    :return: Element
    :rtype: Element Object
    """
    Log.info(f"Finding element with ID {element_id}")
    return driver.find_element_by_id(element_id)

def find_by_xpath(driver, xpath):
    """
    find_by_xpath

    Finds using xpath, an element on a page

    :param driver: Webdriver controller for the web page
    :param xpath: Xpath of the element

    :return: Element
    :rtype: Element Object
    """
    Log.info(f"Finding element with Xpath {xpath}")
    return driver.find_element_by_xpath(xpath)


def fill_in_text_element_by_class(driver, element_class_name, text):
    """
    fill_in_text_element

    Generates a contains string for searching for an element on a page

    :param driver: Webdriver controller for the web page
    :param element_class_name: Class name of the element
    :param text: Text to fill in.
    """
    Log.info(f"Filling in text {text} on element of Class {element_class_name}")
    element = driver.find_element_by_class_name(element_class_name)
    element.send_keys(text)


def fill_in_text_element_by_id(driver, element_id, text):
    """
    fill_in_text_element

    Generates a contains string for searching for an element on a page

    :param driver: Webdriver controller for the web page
    :param element_id: ID of the element
    :param text: Text to fill in.
    """
    Log.info(f"Filling in text {text} on element of ID {element_id}")
    element = driver.find_element_by_id(element_id)
    element.send_keys(text)


def fill_in_text_element_by_xpath(driver, element_xpath, text):
    """
    fill_in_text_element_by_xpath

    Fills in a text field for an element found by xpath

    :param driver: Webdriver controller for the web page
    :param element_xpath: XPath of the element
    :param text: Text to fill in.
    """
    Log.info(f"Filling in text {text} on element of XPath {element_xpath}")
    element = driver.find_element_by_xpath(element_xpath)
    element.send_keys(text)

def get_element_by_xpath(driver, xpath):
    """
    get_element_by_xpath

    Gets an element by it's xpath

    :param driver: Webdriver for the browser
    :param xpath: Xpath of the element
    :return: WebElement object
    """
    Log.info(f"Getting element at xpath {xpath}")
    return driver.find_element_by_xpath(xpath)

def get_elements_by_xpath(driver, xpath):
    """
    get_elements_by_xpath

    Gets a list of elements by an Xpath

    :param driver: Web driver object for the action
    :param xpath: Xpath of the list of elements
    :return: List of WebElements
    """
    Log.info(f"Getting list of elements at xpath {xpath}")
    return driver.find_elements_by_xpath(xpath)

def get_first_element_of_list_by_xpath(driver, xpath):
    """
    get_first_element_of_list_by_xpath

    Calls get_elements_by_xpath and takes first element of the list

    :param driver: Webdriver for the browser
    :param xpath: Xpath for the list of elements
    :return: WebElement object
    """
    Log.info(f"Getting first elements of list in {xpath}")
    element_list = get_elements_by_xpath(driver, xpath)
    return element_list[0]

def generate_contains_string(string_to_search_for):
    """
    generate_contains_string

    Generates a contains string for searching for an element on a page

    :param string_to_search_for: String of the element

    :return The contains string to use in selector
    :rtype: String
    """
    return f'{CONTAINS_TEXT_HEADER}{string_to_search_for}]'

def get_element_xpath_by_text_only(text):
    """
    get_element_xpath_by_text_only

    Finds an element just on it's text value
    :param text:
    :return: WebElement object
    """
    return f'//*/text()="{text}"'

def launch_menu(driver, desired_page, menu_items):
    """
    launch_menu

    Launches a menu item

    :param driver: Webdriver to control page
    :param desired_page: Desired page to be on. If we are already on it, we stay there.
    :param menu_items: List of the menu items to click in order.

    :return: Flag to show that the page has changed to the desired page
    :rtype: Boolean
    """
    Log.info(f"Lunching menu to get us to desired page {desired_page}")
    if driver.title == desired_page:
        return True
    for menu_item in menu_items:
        wait_for_by_id_then_click(driver, menu_item)
        Log.info(f"PAGE TITLE {driver.title}")
    return driver.title == desired_page


def open_url(driver, url):
    """
    open_url

    Opens a URL

    :param driver: Webdriver to control page
    :param url: Desired URL
    """
    Log.info(f"Going to URL {url}")
    driver.get(url)

def setup_driver(browser='chrome'):
    """
    setup_driver

    Sets the driver up for the browser

    :param browser: Browser to use e.g chrome, firefox, ie.

    :return: Browser object for the chosen browser
    :rtype: Webdriver object
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument('ignore-certificate-errors')
    return _setup_driver_options(browser, options)

def take_screenshot(driver, screenshot_name='screenshot.png'):
    """
    take_screenshot

    Utility to take a screenshot. Stores it on the current working directory

    :param driver: Webdriver Object for the browser
    :param screenshot_name: Name of the screenshot file
    :return:
    """
    Log.info(f"Creating screenshot {screenshot_name}")
    driver.save_screenshot(screenshot_name)

def wait_for_page_changes(driver, page_title_to_change_to, wait_for_seconds=60):
    """
    wait_for_page_changes

    Waits for an page to change, subject to timeout specified in wait_for_seconds

    :param driver: Webdriver controller for the web page
    :param page_title_to_change_to: Title of the page we want to go to.
    :param wait_for_seconds: Timeout value for the page to change to the desired page title
    """
    Log.info(f"Current page title is {driver.title}")
    Log.info(f"Waiting {wait_for_seconds} seconds for page to change to {page_title_to_change_to}")
    try:
        WebDriverWait(driver, wait_for_seconds).until(expected_conditions.title_contains(page_title_to_change_to))
    except TimeoutException as e:
        Log.error(f"Timed out with page title at {driver.title}")
        take_screenshot(driver)
        driver.quit()
        raise TimeoutException(f"Timed out with page title at {driver.title}. {e}")
    Log.info(f"Page has changed to {page_title_to_change_to}")


def wait_for_by_id_then_click(driver, element_id, wait_for_seconds=30):
    """
    wait_for_by_id_then_click

    Waits for an element by id to be clickable and clicks it

    :param driver: Webdriver controller for the web page
    :param element_id: ID of the element to interact with.
    :param wait_for_seconds: Timeout value for the element to be clickable
    """
    Log.info(f"Waiting {wait_for_seconds} seconds to be clickable, then clicking element with ID {element_id}")
    WebDriverWait(driver, wait_for_seconds).until(
        expected_conditions.element_to_be_clickable((By.ID, element_id)))
    retries = int(wait_for_seconds / 10)
    wait_seconds = 10
    attempt_number = 1
    while attempt_number <= retries:
        Log.info(f"Trying to click element: Attempt number {attempt_number} of {retries}")
        try:
            click_element_by_id(driver, element_id)
            return
        except Exception as e:
            Log.warning(f"Failed the click. Waiting {wait_seconds} seconds to retry. {e}")
            sleep(wait_seconds)
        attempt_number += 1
    driver.save_screenshot("screenshot.png")
    driver.quit()
    raise FileNotFoundError("Out of retries. Could not click the element")


def wait_for_by_xpath_then_click(driver, element_xpath, wait_for_seconds=40):
    """
    wait_for_by_xpath_then_click

    Waits for an element by xpath to be clickable

    :param driver: Webdriver controller for the web page
    :param element_xpath: Xpath of the element to interact with.
    :param wait_for_seconds: Timeout value for the element to be clickable
    """
    Log.info(f"Waiting {wait_for_seconds} seconds for element with xpath {element_xpath} to appear!")
    WebDriverWait(driver, wait_for_seconds).until(
        expected_conditions.element_to_be_clickable((By.XPATH, element_xpath)))
    click_element_by_xpath(driver, element_xpath)

def wait_for_by_id_then_fill_in(driver, element_id, text, wait_for_seconds=30):
    """
    wait_for_by_id_then_fill_in

    Waits for an element by xpath to be clickable and fills it in with specified text

    :param driver: Webdriver controller for the web page
    :param element_id: ID of the element to interact with.
    :param text: Text to fill into the element
    :param wait_for_seconds: Timeout value for the element to be clickable
    """
    Log.info(f"Trying to fill in text {text} on element with ID {element_id} within {wait_for_seconds} seconds")
    element = WebDriverWait(driver, wait_for_seconds).until(
        expected_conditions.element_to_be_clickable((By.ID, element_id)))
    element.send_keys(text)


def wait_for_by_xpath(driver, element_xpath, wait_for_seconds=40, return_element=False):
    """
    wait_for_by_xpath

    Waits for an element by xpath to be clickable

    :param driver: Webdriver controller for the web page
    :param element_xpath: Xpath of the element to interact with.
    :param wait_for_seconds: Timeout value for the element to be clickable
    """
    Log.info(f"Waiting {wait_for_seconds} seconds for element with xpath {element_xpath} to appear!")
    sleep(wait_for_seconds)
    element = driver.find_elements_by_xpath(element_xpath)
    # WebDriverWait(driver, wait_for_seconds).until(
    #     expected_conditions.elem((By.XPATH, element_xpath)))
    Log.info("Element found")
    if return_element:
        return element


def wait_for_by_xpath_then_fill_in(driver, element_xpath, text, wait_for_seconds=200):
    """
    wait_for_by_xpath_then_fill_in

    Waits for an element by xpath to be clickable and fills it in with specified text

    :param driver: Webdriver controller for the web page
    :param element_xpath: Xpath of the element to interact with.
    :param text: Text to fill into the element
    :param wait_for_seconds: Timeout value for the element to be clickable
    """
    Log.info(f"Filling in text {text} on element with Xpath {element_xpath}")
    element = WebDriverWait(driver, wait_for_seconds).until(
        expected_conditions.element_to_be_clickable((By.XPATH, element_xpath)))
    element.send_keys(text)


def wait_for_by_xpath_then_get_text(driver, element_xpath, wait_for_seconds=30):
    """
    wait_for_by_xpath_then_get_text

    Waits for an element by xpath to be clickable and reads it's text

    :param driver: Webdriver controller for the web page
    :param element_xpath: Xpath of the element to interact with.
    :param wait_for_seconds: Timeout value for the element to be clickable
    """
    Log.info(f"Waiting {wait_for_seconds} seconds, to find element of xpath {element_xpath}")
    label = WebDriverWait(driver, wait_for_seconds).until(
        expected_conditions.element_to_be_clickable((By.XPATH, element_xpath, wait_for_seconds)))
    text = label.text
    Log.info(f"Text returned is {text}")
    return text


def wait_for_element_not_to_be_clickable(driver, element_xpath_or_id, element_type='xpath', wait_interval=5, max_wait_time=60):
    """

    wait_for_element_not_to_be_clickable

    Recursively checks for the element to not be clickable

    :param driver: Webdriver for the browser
    :param element_xpath_or_id: Xpath or ID of the element we want to not be clickable. Defined by element_type
    :param element_type: 'xpath' or 'id' to select the appropriate Webdriver call for find element
    :param wait_interval: Sleep interval between checks
    :param max_wait_time: Timeout for the element to not be clickable
    :return:
    """
    time_waited = 0
    while time_waited < max_wait_time:
        Log.info(f"Waiting {wait_interval} seconds for element with {element_type} {element_xpath_or_id}"
                 f" to NOT be clickable")
        try:
            if element_type == 'xpath':
                find_by_xpath(driver, element_xpath_or_id)
            else:
                find_by_id(driver, element_xpath_or_id)
            Log.warning(
                f"Element is still clickable. Waiting another {wait_interval} seconds. Waited {time_waited} sofar")
            sleep(wait_interval)
            time_waited += wait_interval
        except Exception as e:
            Log.info(f"Element is now not clickable. Returning. {e}")
            return
    take_screenshot(driver)
    raise FileNotFoundError(f"Element still clickable after {max_wait_time}")

def wait_for_element_to_be_clickable(driver, xpath_or_id, element_type='xpath', wait_for_seconds=30):
    """

    :param driver:
    :param xpath_or_id:
    :param element_type:
    :param wait_for_seconds:
    :return:
    """
    Log.info(
        f"Waiting {wait_for_seconds} seconds to be clickable, then clicking element with {element_type} {xpath_or_id}")
    if element_type == 'xpath':
        WebDriverWait(driver, wait_for_seconds).until(
            expected_conditions.element_to_be_clickable((By.ID, xpath_or_id)))
    else:
        WebDriverWait(driver, wait_for_seconds).until(
            expected_conditions.element_to_be_clickable((By.XPATH, xpath_or_id)))

def _setup_driver_options(browser, options):
    """
    _setup_driver_options

    Creates the executable for the browser

    :param browser: Browser to use e.g chrome, firefox, ie.
    :param options: Desired options to use.

    :return: Browser object for the chosen browser
    :rtype: Webdriver object
    """
    global driver
    if browser == 'chrome':  # TODO OTHER BROWSERS
        if OSSE_UI_OPERATING_SYSTEM == "windows":
            path = OSSE_CHROMEDRIVER_WINDOWS_PATH
        elif OSSE_UI_OPERATING_SYSTEM == "linux":
            path = OSSE_CHROMEDRIVER_LINUX_PATH
        else:
            raise NotImplementedError(f"Operating system {OSSE_UI_OPERATING_SYSTEM} not yet supported in testware")
        Log.info(
            f"Setting up {OSSE_UI_OPERATING_SYSTEM} {browser} browser "
            f"with driver executable at {path}")
        driver = webdriver.Chrome(
            options=options,
            executable_path=path)
    Log.info(f"Using browser version {driver.capabilities['browserVersion']}")
    return driver
