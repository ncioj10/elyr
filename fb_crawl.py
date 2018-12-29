from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pickle
import os
import time
import re
import requests as rq


class FacebookCrawler():
    def __init__(self, fb_user, fb_pass):
        # disable notifications request
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.fb_user = fb_user
        self.fb_pass = fb_pass

    def login(self):
        driver = self.driver
        driver.get("https://www.facebook.com/")
        print("Opened Facebook")

        exists = os.path.isfile('./tmp/cookies.pkl')

        try:
            cookies = pickle.load(open("./tmp/cookies.pkl", "rb"))

            for cookie in cookies:
                driver.add_cookie(cookie)
            print("test")

        except:
            email = driver.find_element_by_id("email")
            email.send_keys(self.fb_user)
            print("Entered Email")

            passwd = driver.find_element_by_id("pass")
            passwd.send_keys(self.fb_pass)
            print("Entered Password")

            login_button = driver.find_element_by_id("loginbutton")
            login_button.click()

        time.sleep(2)
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#userNavigationLabel"))
        )
        if len(driver.get_cookies()) > 0:
            pickle.dump(driver.get_cookies(), open("./tmp/cookies.pkl", "wb"))

    def access_event(self, event_id):
        driver = self.driver

        print("Acces Event " + str(event_id))
        driver.get("https://www.facebook.com/events/" + str(event_id))
        guest_list = driver.find_element_by_xpath("//a[contains(@href, '/events/dialog/public_guest_list')]")
        print(guest_list.text)
        guest_list.click()

        guest_list_text = guest_list.text.replace('.', '')

        nums = [int(s) for s in guest_list_text.split() if s.isdigit()]

        time.sleep(4)

        scroll_container = driver.find_elements_by_class_name('uiScrollableAreaContent')
        print(str(len(scroll_container)))

        for i in range((int)(nums[0] * 0.05)):
            print("step ", i)

            scroll_container[1].click()
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(0.5)

        participants_raw = scroll_container[1].find_elements_by_xpath(
            "//a[contains(@data-hovercard,'/ajax/hovercard/hovercard.php?id=')]")

        participants = []
        for i in range(len(participants_raw)):
            p = participants_raw[i]
            if i % 2 == 1:
                name_span = p.find_element_by_tag_name("span")
                name = name_span.text
                gender_result = self.get_gender(name)
                profile_link = p.get_attribute("href")

                participants.append({"name": name, 'profile_link': profile_link, "gender": gender_result["gender"],
                                     "gender_acc": gender_result["scale"]})
                print("name:", name)
                print("profile_link:", profile_link)

        return {"num_going": nums[0], "num_interested": nums[1], "participants": participants}

    def get_gender(self, name):
        names = name.split(" ")

        request_url = "https://api.namsor.com/onomastics/api/json/gender/" + names[0] + "/" + names[-1]

        result = rq.get(request_url)

        return result.json()
