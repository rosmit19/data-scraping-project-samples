import scrapy
import json
from scrapy.http import JsonRequest
import time
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import os.path
import re
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
# from utils import get_currency




# """JAVASCRIPT DISABLE, MAYBE TO_DO USING SELENIUM"""
class TestSpider(scrapy.Spider):
    name = "algonquin"
    file_name = 'Algonquin College CA'
    main_url = "https://flemingcollege.ca"
    token = ""
    data_directory = ""
    course_name, sub_category, category, course_website, duration, duration_term, degree, intake_month, intake_day, apply_month, apply_day, city, study_mode, dom_only, prerequisites, fee_dom, fee_int, fee_year, fee_term, currency, study_load, ielts_overall, ielts_reading, ielts_writing, ielts_listening, ielts_speaking, toefl_overall, toefl_reading, toefl_writing, toefl_listening, toefl_speaking, pte_overall, pte_reading, pte_writing, pte_listening, pte_speaking, eng_overall, eng_test, eng_reading, eng_listening, eng_speaking, eng_writing, course_struct, career, course_des, language, other_requirements = [
        [] for i in range(47)]
    index = 1
    generatepptx = True
    start_urls = ['https://www.algonquincollege.com/future-students/programs/']
    def __init__(self):
        url = 'https://www.algonquincollege.com/future-students/programs/'
        self.driver = webdriver.Chrome()
    def parse(self,response):
        self.driver.get(response.url)
        # xpath = '(//tr[@class="odd"] | //tr[@class="even"]//td//a)'
        # course_content = self.driver.find_elements_by_xpath(xpath)
        course_content = self.driver.find_elements_by_xpath('(//tr[@class="odd"] | //tr[@class="even"])')
        for url in course_content:
            c_url = url.find_element_by_xpath(".//td//a").get_attribute("href")
            c_name = url.find_element_by_xpath('.//td//a').text
            print(c_url)
            cat = url.find_element_by_xpath('.//td[@class=" min-tablet"][1]').text
            loc = url.find_element_by_xpath('.//td[@class=" min-tablet"][2]').text
            DL = url.find_element_by_xpath('.//td[@class=" min-tablet"][3]').text
            content = url.find_element_by_xpath('.//td[@class=" min-tablet"][4]').text.lower()
            try:
                SL = "Both" if content.find("full") != -1 and content.find("part") != -1 else (
                        "Full Time" if content.find("full") != -1 else ("Part Time" if content.find("part") != -1 else ""))
            except:
                SL = ''
            try:
                SM = "Both" if content.find("online") != -1 and content.find("on campus") != -1 else (
                    "Online" if content.find("online") != -1 else "On Campus" if content.find("on campus") != -1 else '')
            except:
                SM =''
            meta = [c_url,c_name,cat,loc,DL,SL,SM]
            yield scrapy.Request(url=c_url, meta={'meta': meta}, callback = self.parse2)
            
        
    def parse2(self,response):
        meta = response.meta['meta']
        c_url,c_name,cat,loc,DL,SL,SM = meta
        # self.course_website.append(response.url)
        try:
            duration_content = response.xpath('//strong[contains(.,"Duration:")]//following::span[1]/text()').get().lower()
            duration = ' '.join(re.findall(r'\d+', duration_content))
            duration_term = "Year" if duration_content.find("years" or "year") != -1 else ("Month" if duration_content.find("month" or "months") != -1 else (
                    "Week" if duration_content.find("week") != -1 else ("Day" if duration_content.find("day") != -1 else (
                        "Hour" if duration_content.find("hour") != -1 else (
                            "Semester" if duration_content.find("semesters") != -1 else ("Term" if duration_content.find("term") != -1 else ""))))))
        except:
            duration_content = ''
            duration = ''
            duration_term = ''
        try:
            des = ' '.join(response.xpath('//div[@id="overview"]//div[@class="col-sm-8"]//*[following-sibling::h3[contains(text(),"SUCCESS FACTORS")]] | //div[@id="overview"]//div[@class="col-sm-8"]//*[following-sibling::h3[contains(text(),"Success Factors")]]').getall()).strip()
        except:
            des = ''
        try:
            CS = response.xpath('//div[@class="courses-container"]').get()
        except:
            CS = ''
        try:
            career = response.xpath('//h3[contains(text(),"Careers")]//following-sibling::p[1]').get()
        except:
            career = ''
        try:
            OR = ' '.join(response.xpath('//div[@id="newtext"]//ul | //div[@id="newtext"]//p').getall()).strip()
        except:
            OR =''
        try:
            language_content = response.xpath('(//ul/li[contains(text(),"IELTS")]) [1]/text()').get()
            IELTS = language_content.split('OR TOEFL') [0]
            IELTS_list = re.findall(r'(\d+\.\d+?)|\.\d+', (IELTS))
            i_len = len(IELTS_list)
        except:
            IELTS = ""
            IELTS_list = []
        # and "an overall score of" in IELTS and "with no score less than" in IELTS
        try:  
            if i_len == 2 :
                IELTS = [IELTS_list[0],IELTS_list[1],IELTS_list[1],IELTS_list[1],IELTS_list[1]]
            else:
                IELTS = ['','','','','']
        except:
            IELTS = ['','','','','']

        try:
            TOEFL = language_content.split('OR TOEFL') [1].split('in each component:')[0]
            TOEFL_list = re.findall(r'\b\d+\b',TOEFL)
            t_len = len(TOEFL_list)
            if t_len == 2:
                TOEFL = [TOEFL_list[0], TOEFL_list[1],TOEFL_list[1],TOEFL_list[1],TOEFL_list[1]]
            else:
                TOEFL = ['','','','','']
        except:
            TOEFL = ['','','','','']
            TOEFL_list = []

        self.course_name.append(c_name)
        self.course_website.append(c_url)
        self.course_des.append(des)
        self.career.append(career)
        self.course_struct.append(CS)
        self.other_requirements.append(OR)
        self.duration.append(duration)
        self.duration_term.append(duration_term)
        self.degree.append(DL)
        self.study_load.append(SL)
        self.city.append(loc)
        self.study_mode.append(SM)
        self.category.append(cat)
        self.ielts_overall.append(IELTS[0])
        self.ielts_listening.append(IELTS[1])
        self.ielts_speaking.append(IELTS[2])
        self.ielts_writing.append(IELTS[3])
        self.ielts_reading.append(IELTS[4])
        self.toefl_overall.append(TOEFL[0])
        self.toefl_listening.append(TOEFL[1])
        self.toefl_speaking.append(TOEFL[2])
        self.toefl_writing.append(TOEFL[3])
        self.toefl_reading.append(TOEFL[4])

    