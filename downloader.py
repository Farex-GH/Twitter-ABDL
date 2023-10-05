from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from collections import namedtuple
from urllib.request import urlretrieve

import time
import argparse

class Downloader:
    username = ""
    password = ""
    page = ""
    download_path = ""
    finish_on_url = ""
    finish_on_name = ""
    driver = any
    wait = any 

    def __init__(self, username, password, page, download_path=".", finish_on_url="", finish_on_name = ""):
        self.username = username
        self.password = password
        self.page = page
        self.download_path = download_path
        self.finish_on_url = finish_on_url
        self.finish_on_name = finish_on_name

        # Append a slash if it isn't there. Windows can handle '\\' or '/', so just do '/' because it's better.
        if (self.download_path[:-1] != '/' and self.download_path[:-1] != '\\'):
            self.download_path += '/'

        # Grab the web page
        self.driver = webdriver.Firefox()
        self.driver.get(page)
        assert "Twitter" in self.driver.title
        # Init element waiting timeout
        self.wait = WebDriverWait(self.driver, 5)
        # We need this so each transaction has time to load, but don't make it too long.
        # If it's too long, the timeout when looking for videos is also long and annoying.
        self.driver.implicitly_wait(1)
        # Put the page on full display. Have no shame.
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def login(self):
        # Send username
        elem = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@autocomplete='username']")))
        elem.clear()
        elem.send_keys(self.username)
        elem.send_keys(Keys.RETURN)

        # Send password.
        elem = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@autocomplete='current-password']")))
        elem.clear()
        elem.send_keys(self.password)
        elem.send_keys(Keys.RETURN)

    def get_image_links(self):
        img_elems = self.driver.find_elements(By.XPATH, "//img[@class='css-9pa8cd'][@alt='Image']")
        image_link = namedtuple('ImageLink', 'url image_name')
        image_links = []

        for image in img_elems:
            # These seems to happen when autoscroll grabs the same image several times in a row, each having
            # a different context ID. We can just print that it happened and ignored it, because eventually we'll
            # parse the image using the current context ID.
            try:
                image_url = image.get_attribute("src")
            except StaleElementReferenceException:
                print("Tried to parse a stale element on element " + image.id)
                continue

            # Trim off the '&format=small' at the end.
            image_url = image_url.partition("&name=")[0]
            extension = image_url.partition("?format=")[-1]
            # Grab '/base64-image-name?format=jpg'
            start_index = image_url.rindex("/")
            # '/base64-image-name'
            end_index = image_url.rindex("?")
            # 'base64-image-name'
            image_name = image_url[1+start_index:end_index]
            # 'base64-image-name.extension'
            image_name += ("." + extension)

            # Add '&name=large' to grab the full resolution image.
            image_url += "&name=large"

            img = image_link(image_url, image_name)
            image_links.append(img)
            print("Grabbed URL " + image_url + " and image name " + image_name)
        return image_links
        
    def get_video_links(self):
        video_elems = self.driver.find_elements(By.XPATH, "//video[@aria-label='Embedded video'][@type='video/mp4']")
        video_link = namedtuple('ImageLink', 'url image_name')
        video_links = []

        # There's no videos, just bail out.
        if video_elems is None:
            return video_links

        for video in video_elems:
            # These seems to happen when autoscroll grabs the same image several times in a row, each having
            # a different context ID. We can just print that it happened and ignored it, because eventually we'll
            # parse the image using the current context ID.
            try:
                video_url = video.get_attribute("src")
            except StaleElementReferenceException:
                print("Tried to parse a stale element on element " + video.id)
                continue

            # Grab '/base64-video-name.mp4'
            start_index = video_url.rindex("/")
            # 'base64-video-name.mp4'
            video_name = video_url[1+start_index:]

            video = video_link(video_url, video_name)
            video_links.append(video)
            print("Grabbed URL " + video_url + " and video name " + video_name)
        return video_links
    
    def download_images_until_done(self):
        finished = False
        retry_grab = 0
        parsed = {}

        while (not finished):
            parsed_in_batch = False
            image_urls = self.get_image_links()
            image_urls.extend(self.get_video_links())

            # Grab every image in this batch
            for image_url in image_urls:
                # We've already parsed this, skip it. This occurs naturally due to infinite scroll.
                if image_url.url in parsed:
                    continue
                # We're done going through all of the images that we need to, exit
                if image_url.url == self.finish_on_url or image_url.image_name == self.finish_on_name:
                    finished = True
                    break

                # Download the image and say we parsed it.
                urlretrieve(image_url.url, self.download_path + image_url.image_name)
                parsed[image_url.url] = True
                print("Downloaded " + image_url.url + " to " + self.download_path + image_url.image_name)
                parsed_in_batch = True
            
            # If we couldn't grab any new images after a few attempts, we're probably at the bottom of the page and
            # should bail out.
            if (retry_grab == 3):
                finished = True
            if (not parsed_in_batch):
                time.sleep(.5)
                retry_grab += 1
            else:
                retry_grab = 0

            # Scroll down and load more images
            self.scroll_page()
    
    def scroll_page(self):
        # Go slow or we might miss things.
        self.driver.execute_script("window.scrollBy(0,1080)")
        # Let things load
        time.sleep(.1)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", type=str, help="The username of your Twitter account")
    parser.add_argument("-p", "--password", type=str, help="The password of your Twitter account")
    parser.add_argument("--page", type=str, help="The URL of the page you are trying to download from")
    parser.add_argument("--download_path", type=str, help="The path where you want images to be saved", default=".")
    parser.add_argument("--finish_on_url", type=str,
                        help="The URL the downloader will exit on when seen. " +
                        "Should be in the format of 'https://pbs.twimg.com/media/base64-name?format=jpg&name=large'. " +
                        "Used to prevent downloading someone's entire page.", default="")
    parser.add_argument("--finish_on_name", type=str,
                        help="The name of the image (plus extension) the downloader will exit on when seen. " +
                        "For example, on the URL 'https://pbs.twimg.com/media/base64-name?format=jpg&name=large', the " +
                        "image name will be 'base64-name.jpg'. " +
                        "Used to prevent downloading someone's entire page.", default="")

    args = parser.parse_args()

    downloader = Downloader(args.username, args.password, args.page, args.download_path,
                            args.finish_on_url, args.finish_on_name)
    downloader.login()
    downloader.download_images_until_done()

if __name__ == "__main__":
    main()  