import scrapy
import json
from scrapy.http import JsonRequest
import time
from bs4 import BeautifulSoup
import os.path
import re
import numpy as np
import pandas as pd


class TestSpider(scrapy.Spider):
    name = "cmu"
    file_name = 'Coast mountainsssss college CA'
    main_url = "https://www.coastmountaincollege.ca/"
    token = ""
    data_directory = ""
    course_name, sub_category, category, course_website, duration, duration_term, degree, intake_month, intake_day, apply_month, apply_day, city, study_mode, dom_only, prerequisites, fee_dom, fee_int, fee_year, fee_term, currency, study_load, ielts_overall, ielts_reading, ielts_writing, ielts_listening, ielts_speaking, toefl_overall, toefl_reading, toefl_writing, toefl_listening, toefl_speaking, pte_overall, pte_reading, pte_writing, pte_listening, pte_speaking, eng_overall, eng_test, eng_reading, eng_listening, eng_speaking, eng_writing, course_struct, career, course_des, language, other_requirements = [
        [] for i in range(47)]
    index = 1
    generatepptx = True

    def start_requests(self):
        url = "https://www.coastmountaincollege.ca/programs/programs"
        yield scrapy.Request(url=url, callback=self.parse1)

    def parse1(self, response):
        # courses_list = response.xpath('//div[@class="item-full-link"]//a')
        courses_list = response.xpath('//div[@class="list-item-detail"]')
        for url in courses_list:
            c_url = url.xpath('.//div[@class="item-full-link"]//a/@href').get()
            try:
                duration_content = url.xpath(
                    './/div[@class="item-pro-length"]//text()').get()
                duration = ''.join(re.findall(r'\d+', duration_content))
                duration_term = "Year" if duration_content.find("year") != -1 else ("Month" if duration_content.find("month") != -1 else (
                    "Week" if duration_content.find("week") != -1 else ("Day" if duration_content.find("day") != -1 else (
                        "Hour" if duration_content.find("hour") != -1 else (
                            "Semester" if duration_content.find("semester") != -1 else ("Term" if duration_content.find("term") != -1 else ""))))))
            except:
                duration = ''
                duration_term = '' 
            # print('********')
            print(duration)

            try:
                intake_content = url.xpath(
                    './/div[@class="item-pro-intake"]//text()').get().lower()
                IM1 = re.findall('fall|spring|winter|summer|september|october|march|january|february|april|may|june|july|august|november|december',
                                 str(intake_content))
                intakes = ','.join(map(str.capitalize, set(IM1)))
            except Exception as e:
                print(e)
                intake_content = ''
                intakes = ''
            # print(intakes)
            try:
                DL = url.xpath(
                    './/div[@class="item-pro-cert-type"]//text()').get().strip()
            except:
                DL = ''
            try:
                description = ' '.join(
                    url.xpath('.//div[@class="item-desc"]//text()').getall()).strip()
            except:
                description = ''
            meta = [duration, duration_term, intakes, DL, description]
            if 'https:' in c_url:
                yield scrapy.Request(url=c_url, meta={'meta': meta}, callback=self.parse2)
            else:
                yield scrapy.Request(url=self.main_url + c_url, meta={'meta': meta}, callback=self.parse2)

    def parse2(self, response):
        meta = response.meta['meta']
        duration, duration_term, intakes, DL, description = meta
        c_name = response.xpath(
            '//h1[@class="page-title"]//text() | //h1[@id="cphMain_ctl03_ctl00_ctl00_detailContainer_mainShortTextFieldLiteral_0"]//text() | //div[@class="sfContentBlock"]//h1/text()').get()
        try:
            loc_content = ','.join(response.xpath(
                "//caption[contains(text(), 'Dates and Locations')]//parent::table//th[contains(text(),'Location')]//parent::tr//parent::thead//following-sibling::tbody//td[2]//text()").getall()).strip().split(',')
            if not loc_content:
                loc_content = ','.join(response.xpath(
                    "//h2[contains(.,'Dates and location')]//following-sibling::table[1]//td[1]/text()").getall()).strip().split(',')
            print('********')
            print(loc_content)
            loc = set(loc_content)
            location = re.sub("}|{|'", "", str(loc))
        except:
            loc_content = ''
            loc = ''
        
        try:
            CS = response.xpath(
                '//div[@id="programoutlinetextcontainer"]').get().strip()
        except:
            CS = ''
        try:
            OR = response.xpath(
                '//div[@id="admissionrequirementstextcontainer"]').get().strip()
        except:
            OR = ''
        try:
            dom_fee = response.xpath("//tr[contains(.,'Total:')]//td[@class='column1']//text() | //tr[contains(.,'Total program cost:')]//td[@class='column1']//text() | //tr[contains(.,'Program Costs:')]//td[@class='column1'] | //tr[contains(.,'Program Cost:')]//td[@class='column1']//text() | //tr[contains(.,'Total program cost:')]//td[@class='column1']//text()").get().replace('$', '').replace(',', '')
            int_fee = response.xpath("//tr[contains(.,'Total:')]//td[@class='column2']//text() | //tr[contains(.,'Total program cost:')]//td[@class='column2']//text() | //tr[contains(.,'Program Costs:')]//td[@class='column2'] | //tr[contains(.,'Program Cost:')]//td[@class='column2']//text() | //tr[contains(.,'Total program cost:')]//td[@class='column2']//text()").get().replace('$', '').replace(',', '')
        except:
            dom_fee = ''
            int_fee = ''
        try:
            career = response.xpath(
                '//h3[contains(.,"Career opportunities")]//following-sibling::*[following-sibling::h3[2]] | //h3[contains(.,"Career opportunities")]//following-sibling::div').get().strip()
        except:
            career = ''

        try:
            IELTS = response.xpath(
                "//h3[contains(text(),'English Language Requirements')]//following-sibling::ul//li[contains(text(), 'IELTS')]/text()[1]").get()
            IELTS_list = re.findall(r'(\d+\.\d+?)|\.\d+', (IELTS))
            i_len = len(IELTS_list)
        except:
            IELTS = ""
            IELTS_list = []
        try:
            if i_len == 2 and IELTS.find('with no bands lower than'):
                IELTS = [IELTS_list[0], IELTS_list[1],
                         IELTS_list[1], IELTS_list[1], IELTS_list[1]]

        except:
            IELTS = ['', '', '', '', '']
        self.course_name.append(c_name)
        self.course_website.append(response.url)
        self.course_des.append(description)
        self.career.append(career)
        self.course_struct.append(CS)
        self.other_requirements.append(OR)
        self.duration.append(duration)
        self.duration_term.append(duration_term)
        self.degree.append(DL)
        self.fee_int.append(int_fee)
        self.fee_dom.append(dom_fee)
        self.intake_month.append(intakes)
        self.city.append(location)
        self.fee_term.append("Full Course" if dom_fee or int_fee else '')
        self.fee_year.append('2021' if dom_fee or int_fee else '')
        self.currency.append("CAD" if dom_fee or int_fee else '')
        self.ielts_overall.append(IELTS[0])
        self.ielts_listening.append(IELTS[1])
        self.ielts_speaking.append(IELTS[2])
        self.ielts_writing.append(IELTS[3])
        self.ielts_reading.append(IELTS[4])
