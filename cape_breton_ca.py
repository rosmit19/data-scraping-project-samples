import scrapy
import json
from scrapy.http import JsonRequest
import time
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import os.path
import re
import numpy as np
import pandas as pd

class TestSpider(scrapy.Spider):
    name = "cbu"
    file_name = 'Cape Breton University CA'
    main_url = "https://www.cbu.ca/"
    token = ""
    data_directory = ""
    course_name, sub_category, category, course_website, duration, duration_term, degree, intake_month, intake_day, apply_month, apply_day, city, study_mode, dom_only, prerequisites, fee_dom, fee_int, fee_year, fee_term, currency, study_load, ielts_overall, ielts_reading, ielts_writing, ielts_listening, ielts_speaking, toefl_overall, toefl_reading, toefl_writing, toefl_listening, toefl_speaking, pte_overall, pte_reading, pte_writing, pte_listening, pte_speaking, eng_overall, eng_test, eng_reading, eng_listening, eng_speaking, eng_writing, course_struct, career, course_des, language, other_requirements = [
        [] for i in range(47)]
    index = 1
    generatepptx = True

    def start_requests(self):
        url = "https://www.cbu.ca/academics/programs/"
        yield scrapy.Request(url=url, callback=self.parse1)
    def parse1(self,response):
        content_list = response.xpath("//div[@id='ap-search-results']//a[contains(.,'View Program Page')]")
        content_list = response.xpath('//div[@id="ap-search-results"]//article')
        for url in content_list:
            c_url = url.xpath('.//a[contains(.,"View Program Page")]/@href').get()
            c_name = url.xpath('.//h1/text()').get()
            print('********8')
            print(c_name)
            print('********8')
            meta = [c_name]
            yield scrapy.Request(url=c_url, meta={'meta':meta}, callback=self.parse2)
    def parse2(self, response):
        # self.course_website.append(response.url)
        print(response.url)
        meta = response.meta['meta']
        print(meta[0])
        content_details = response.xpath("(//h2[contains(text(), 'Program Snapshot')])//following-sibling::ul[1]")
        DL = ','.join(response.xpath("//small[contains(text(),'Program Types:')]//following-sibling::span//a/text()").getall())
        try:
            duration_content = ','.join(response.xpath("//small[contains(text(),'Program Duration:')]//following-sibling::span//a/text()").getall()).lower()
            duration = ' to '.join(re.findall(r'\d+', duration_content))
            duration_term = "Year" if duration_content.find("year") != -1 else ("Month" if duration_content.find("month") != -1 else (
                    "Week" if duration_content.find("week") != -1 else ("Day" if duration_content.find("day") != -1 else (
                        "Hour" if duration_content.find("hour") != -1 else (
                            "Semester" if duration_content.find("semester") != -1 else ("Term" if duration_content.find("term") != -1 else ""))))))
        except:
            duration = ''
            duration_term=''
        cat = response.xpath("//small[contains(text(),'Fields of Study:')]//following-sibling::span//a/text()").get()
        try:
            description = ' '.join(response.xpath("(//h2[contains(text(), 'Program Snapshot')])//parent::div/following-sibling::p[following-sibling::p[contains(@style, 'text')]]").getall()).strip()
            if not description:
                description = ' '.join(response.xpath("(//h2[contains(text(), 'Program Snapshot')])//parent::div/following-sibling::p[following-sibling::div[2]]").getall()).strip()
        except:
            description = ''
        try:
            int_fee = response.xpath("(//h2[contains(text(), 'tuition')])//following-sibling::ul[1]/li[contains(.,'International')]/a/text()").get().replace('$', '').replace(',', '').replace('per year','')
            print('****************')
            print(int_fee)
        except Exception as e:
            print(e)
            int_fee = ''
        try:
            dom_fee = response.xpath("(//h2[contains(text(), 'tuition')])//following-sibling::ul[1]/li[contains(.,'Canada')]/a/text()").get().replace('$', '').replace(',', '').replace('per year','')
            if not dom_fee:
                dom_fee = response.xpath("(//h2[contains(text(), 'tuition')])//following-sibling::ul[1]/li[contains(.,'off-campus' )]//a/span/text()").get().replace('$', '').replace(',', '').replace('per year')
            print('****************')
            print(dom_fee)
        except Exception as e:
            print(e)
            dom_fee = ''
        try:
            fee_term = 'Year'if int_fee.find('year') and dom_fee.find('year') != -1 else ''
        except:
            fee_term = ''
        try:
            career = response.xpath("//h2[contains(.,'Possible Career Paths')]//following-sibling::ul[1]").get().strip()
        except:
            career = ''
        try:
            OR = response.xpath("//h1[contains(.,'Admission Requirements')]//following::div[contains(@class, 'requirements-block requirements-international')]").get().strip()
        except:
            OR = ''
        
        self.duration_term.append(duration_term)
        self.course_website.append(response.url)
        self.course_name.append(meta[0])
        self.category.append(cat)
        self.other_requirements.append(OR)
        self.degree.append(DL)
        self.course_des.append(description)
        self.career.append(career)
        self.duration.append(duration)
        self.fee_dom.append(dom_fee)
        self.fee_int.append(int_fee)
        self.fee_term.append(fee_term)
        self.fee_year.append('2021' if int_fee else '')
        self.currency.append("CAD" if int_fee else '')



        
        




        