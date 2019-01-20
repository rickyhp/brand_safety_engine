import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import mimetypes
import os, errno
import argparse
from selenium.webdriver.support.wait import WebDriverWait
import threading
from PIL import Image
import logging
from image_downloader import Download_Image
from selenium.common.exceptions import TimeoutException
import image_utils
import directory_utils
from directory_utils import Folder_Utils
from sys import platform
import uuid
import shutil
import tempfile
from threading import Lock, Thread
import multiprocessing as mp
from docutils.nodes import target
import path_config
import settings

lock = Lock()
procs = []
terminate = False
firefox_path = ''
if platform == "linux" or platform == "linux2":
    firefox_path = os.path.abspath('./tools/linux/geckodriver')
if platform == "win32":
    firefox_path = os.path.abspath('./tools/windows/geckodriver.exe')


options = webdriver.FirefoxOptions()
options.add_argument('-headless')
profile = webdriver.FirefoxProfile(profile_directory=path_config.firefox_profile_director)
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False) 
browser = webdriver.Firefox(executable_path=firefox_path, firefox_options=options, firefox_profile=profile)
browser.install_addon(path=path_config.ublock_firefox)
browser.set_page_load_timeout(3)

class Scraping_Image(object):
    def __init__(self, url, dest_folder=''):
        self.url = url
        self.dest_folder = dest_folder 
        print("initialize")
#         options = webdriver.FirefoxOptions()
#         options.add_argument('-headless')
#         profile = webdriver.FirefoxProfile(profile_directory=path_config.firefox_profile_director)
#         self.browser = webdriver.Firefox(executable_path=firefox_path, firefox_options=options, firefox_profile=profile)
#         self.browser.install_addon(path=path_config.ublock_firefox)
#         self.browser.set_page_load_timeout(3)
    
    def _download(self, data, folderName, lock, terminate):
        image_downloader = Download_Image(data, folderName, self.url)
        image_downloader.downloadImages(lock, terminate)
    
    def run(self):
        i = 0
        print('run')
        folderName = self.url if self.dest_folder == '' else self.dest_folder
        try:
#             self.browser.get(self.url)
            browser.get(self.url)
        except TimeoutException:
            browser.execute_script("window.stop();")
        print('get source')
        print(browser.title)
        browser.maximize_window()
        print('maximize window')
        pause = 3
        data=None
        folder=None
        screenshot_name = None
        lastHeight = browser.execute_script("return document.body.scrollHeight")
        browser.set_window_size(1554, lastHeight)
        print(lastHeight)
        try:
            for t in range(3):
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")              
                time.sleep(pause)
                lastHeight = browser.execute_script("return document.body.scrollHeight")
                browser.set_window_size(1554, lastHeight)
            data = browser.page_source
            dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
            folder = os.path.join(dir_path, folderName)
            dir_helper = Folder_Utils()
            dir_helper.createEmptyFolder(folder)
            screenshot_name = str(uuid.uuid4()) + '.png'
            
            browser.get_screenshot_as_file(screenshot_name)
        except Exception as  e:
            print('error in scraping : ' + e.__str__())
            pass
        finally:            
#             self.browser.quit()
            if data is not None and folder is not None and screenshot_name is not None:
                t1 = Thread(target=self._download, args=(data, folderName, lock, terminate))
                t2 = Thread(target=image_utils.slice_image, args=(self.url, folderName, os.path.join(folder, "slices"), screenshot_name, settings.slice_width,settings.slice_height,settings.slice_step, lock, terminate))
                t1.start()
                t2.start()
                t1.join()
                t2.join()              
            
            return True
#             
# scraping = Scraping_Image('https://www.pexels.com/search/alcohol/', os.path.join('www.pexels.com','1'))
# scraping.run()

