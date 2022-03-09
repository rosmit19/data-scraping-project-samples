# coding: utf-8

import scrapy
import re
import calendar
import time
import pandas as pd


class MySpider(scrapy.Spider):
    name = "concordia"
    file_name = "Concordia University"
    token = ""
    data_directory = ""
    main_url = "https://www.concordia.ca"
    course_name, sub_category, category, course_website, duration, duration_term, degree, intake_month, intake_day, apply_month, apply_day, city, study_mode, dom_only, prerequisites, fee_dom, fee_int, fee_year, fee_term, currency, study_load, ielts_overall, ielts_reading, ielts_writing, ielts_listening, ielts_speaking, toefl_overall, toefl_reading, toefl_writing, toefl_listening, toefl_speaking, pte_overall, pte_reading, pte_writing, pte_listening, pte_speaking, eng_overall, eng_test, eng_reading, eng_listening, eng_speaking, eng_writing, course_struct, career, course_des, language, other_requirements = [
        [] for i in range(47)]
    index = 1
    generatepptx = True

    def start_requests(self):
        ug_url = "https://www.concordia.ca/admissions/undergraduate/programs.html"
        pg_url = "https://www.concordia.ca/admissions/graduate/programs.html"
        cont_url = "https://www.concordia.ca/cce/programs.html"
        urls = [ug_url,pg_url,cont_url]
        for url in urls:
            yield  scrapy.Request(url = url,callback=self.parse1)

    def parse1(self, response):
        course_url = response.xpath("//span[contains(text(),'View program details')]/parent::a/@href | //div[@class='title section'][not(contains(.,'Language'))]/following-sibling::div//a[not(contains(.,'Part')) and not(contains(.,'English')) and not(contains(.,'French'))]/@href").getall()
        for url in course_url:
            yield scrapy.Request(url=self.main_url+url,callback=self.parse2)
    def parse2(self, response):
        # print("**********")
        url = response.url
        if "online-workshops.html" in url:
            url = ""
            return
        # print(url)
        self.course_website.append(url)

        try:
            CN = response.xpath("//h1[contains(@class,'hero-title')]/text() | //div[@class='title section']//h1/text()").get().strip()
        except:
            pass
        self.course_name.append(CN)

        #Category
        try:
            CG = response.xpath("//div[contains(text(),'Department')]/following-sibling::div[1]//a/text()").get()
        except:
            pass
        self.category.append(CG)

        #Sub Category
        try:
            SC = response.xpath("//div[contains(text(),'Faculty')]/following-sibling::div[1]//a/text()").get()
        except:
            pass
        self.sub_category.append(SC)

        #Degree Level
        try:
            DL = response.xpath("(//div[contains(text(),'Degree')])/following-sibling::div[following-sibling::div[contains(.,'Department')]]//text()").get()
        except:
            pass
        self.degree.append(DL)

        # 		Location
        try:
            LOC = response.xpath("//div[contains(text(),'Primary campus')]/following-sibling::div//text()").get()
        except:
            pass
        self.city.append(LOC)

            # Duration

        try:
            DR = response.xpath("//h3[contains(text(),'Upcoming')]/following-sibling::form//div[contains(text(),'Duration')]/following-sibling::text()").get()
            if not DR:
                DR = " ".join(response.xpath(
                "//div[contains(text(),'Duration')]/following-sibling::div//text()").getall())
            DR = re.findall(r'\b\d{1,3}\b', DR)
            DR =" to ".join(DR[:2]) if DR else ''
        except:
            pass
        self.duration.append(DR)

        # Duration Term
        try:
            DT = response.xpath("//h3[contains(text(),'Upcoming')]/following-sibling::form//div[contains(text(),'Duration')]/following-sibling::text()").get()
            if not DT:
                DT = "\n".join(response.xpath(
                "//div[contains(text(),'Duration')]/following-sibling::div//text()").getall())
            DT = DT.lower()
            DT = "Year" if DT.find("year") != -1 else ("Month" if DT.find("month") != -1 else (
                "Week" if DT.find("week") != -1 else ("Day" if DT.find("day") != -1 else (
                    "Hour" if DT.find("hour") != -1 else (
                        "Semester" if DT.find("semester") != -1 else ("Term" if DT.find("term") != -1 else ""))))))
        except:
            pass
        self.duration_term.append(DT)

        # Intake Month
        try:
            IM1 = " ".join(response.xpath(
                "//div[contains(text(),'Start')]/following-sibling::div//text()").extract())
            if not IM1:
                IM = " ".join(response.xpath("//h6[@class='burgundy'][contains(.,'2021')]//text()").getall()).lower()
                IM1 = re.findall(
                    'sep|oct|mar|jan|feb|apr|may|jun|jul|aug|nov|dec', unicode(IM))
                IM1 = ','.join(map(unicode.capitalize, ((IM1)))).replace("Sep", "September").replace("Oct","October").replace(
                    "Mar", "March").replace("Jan", "January").replace("Feb", "February").replace("Apr", "April")\
                    .replace("Jun", "June").replace("Jul", "July").replace("Aug","August").replace("Nov", "November").replace("Dec", "December")
        except:
            pass
        self.intake_month.append(IM1)

        # Intake Day
        try:
            ID = ""
            ID = (" ".join(response.xpath(
                "//h6[@class='burgundy'][contains(.,'2021')]//text()").extract()).lower())
            ID = re.findall(r'\b\d{1,2}\b', ID)
            ID = (ID) if ID else ''
            ID = (", ".join(set(ID)))
        except:
            pass
        self.intake_day.append(ID)

        #Overview
        try:
            OV = response.xpath("//h2[contains(text(),'Why')]/ancestor::div[@class='title section']/following-sibling::div").get()
            if not OV:
                OV = "\n".join(response.xpath("//div[@class='wysiwyg parbase section'][following-sibling::div[@class='title section']//h2[contains(.,'Your take')]]").getall())
            if not OV:
                OV = "\n".join(response.xpath("(//div[contains(@class,'picturefill-container')])[1]//span").getall())
            if not OV:
                OV = response.xpath(u"//div[@class='title section'][contains(.,'overview')]/following-sibling::div | //div[@class='title section'][contains(.,'Présentation')]/following-sibling::div").get()

        except:
            pass
        self.course_des.append(OV)
        # Course Structure

        try:
            CS = "\n".join(response.xpath("//div[@class='title section'][contains(.,'Program structure')]/following-sibling::div//h3//a/ancestor::div[@class='group panel xlarge']/parent::div").getall())
            if not CS:
                CS = "\n".join(response.xpath("//div[@class='title section'][contains(.,'Program structure')]/following-sibling::div[contains(.,'Program')]").getall())
            if not CS:
                CS = "\n".join(response.xpath("//div[@class='title section'][contains(.,'Compulsory') or contains(.,'Elective')]/following-sibling::div").getall())
            if not CS:
                CS = "\n".join(response.xpath("//div[@class='title section'][contains(.,'Modules')]/following-sibling::div[following-sibling::div//h2[@class='burgundy']]").getall())
            if not CS:
                CS = "\n".join(response.xpath("//div[@class='title section'][contains(.,'Program structure')]/following-sibling::div//p[not(contains(.,'United States'))] | //div[@class='title section'][contains(.,'programme')]/following-sibling::div").getall())
        except:
            pass
        self.course_struct.append(CS)

    # Study Load
        try:
            SL = " ".join(response.xpath(
                "//h3[contains(text(),'Upcoming dates')]/ancestor::div[contains(@class,'parbase')]//h3").getall()).lower()
            SL = "Both" if SL.find("full") != -1 and SL.find("part") != -1 else (
                "Full Time" if SL.find("full") != -1 else ("Part Time" if SL.find("part") != -1 else ""))
        except:
            pass
        self.study_load.append(SL)

        #Other requirments
        try:
            OR = "\n".join(response.xpath("//div[@class='title section'][contains(.,'dmission')]/following-sibling::div[following-sibling::div[contains(@class,'button')]]").getall())
            if not OR:
                OR = "\n".join(response.xpath("//div[@class='title section'][contains(.,'dmission')]/following-sibling::div[@class='box parbase section']//div/*[following-sibling::div[contains(.,'You must meet')]]").getall())
            if not OR:
                OR = "\n".join(response.xpath("//div[@class='title section'][contains(.,'dmission')]/following-sibling::div//div[following-sibling::div[contains(.,'You must ')]]").getall())
        except:
            pass
        self.other_requirements.append(OR)

        # Apply Month
        try:
            AM = " ".join(response.xpath(
                "//span[@class='xlarge-text']//b[1]//text()").extract()).lower().replace(
                ".", "")
            if not AM:
                AM = " ".join(response.xpath("//span[@class='xlarge-text']/text()").getall())
            AM1 = re.findall(
                'sep|oct|mar|jan|feb|apr|may|jun|jul|aug|nov|dec', unicode(AM))
            AM1 = ','.join(map(unicode.capitalize, ((AM1)))).replace("Sep", "September").replace("Oct",
                                                                                                    "October").replace(
                "Mar", "March").replace("Jan", "January").replace(
                "Feb", "February").replace("Apr", "April").replace("Jun", "June").replace("Jul", "July").replace(
                "Aug", "August").replace("Nov", "November").replace("Dec", "December")
        except:
            pass
        self.apply_month.append(AM1)

        # Apply Day
        try:
            AD = " ".join(response.xpath(
                "//span[@class='xlarge-text']//b[1]//text()").getall()).lower()
            if not AD:
                AD = " ".join(response.xpath("//span[@class='xlarge-text']/text()").getall())
            AD = re.findall(r'\b\d{1,2}\b', AD)
            AD = (", ".join(AD)) if AD else ''
        except:
            pass
        self.apply_day.append(AD)

#         Career
        try:
            CR = "\n".join(response.xpath("//div[@class='title section'][contains(.,'After')]/following-sibling::div[following-sibling::div[contains(.,'Learn')]]").getall())
            if not CR:
                CR = "\n".join(response.xpath(
                    "//div[@class='title section'][contains(.,'After')]/following-sibling::div").getall())
        except:
            pass
        self.career.append(CR)

        #Domestic Fee
        try:
            DF = response.xpath("//div[contains(text(),'Regular')]/following-sibling::text()[contains(.,'$')]").get()
            DF = self.get_currency(DF)
        except:
            pass
        self.fee_dom.append(DF)
        self.fee_term.append(DT if DF else "")
        self.fee_year.append("2021" if DF else "")
        self.currency.append("CAD" if DF else "")

        # IELTS
        try:
            IELTS = " ".join(response.xpath("//*[contains(text(),'IELTS')]//text()").getall()).split("IELTS")[1]
            IELTS_list = re.findall(r' [5-8]\.[0|5]| [5-8]', (IELTS))
            i_len = len(IELTS_list)
            IELTS = [IELTS_list[0], "", "", "", ""] if i_len == 1 else (
                [IELTS_list[0], IELTS_list[1], IELTS_list[1], IELTS_list[1], IELTS_list[1]] if i_len == 2 else (
                    [IELTS_list[0], IELTS_list[1], IELTS_list[2], IELTS_list[1], IELTS_list[1]] if i_len == 3 else [
                        "", "", "", "", ""]))
        except:
            IELTS = ["", "", "", "", ""]
        self.ielts_overall.append(IELTS[0])
        self.ielts_reading.append(IELTS[1])
        self.ielts_writing.append(IELTS[2])
        self.ielts_listening.append(IELTS[3])
        self.ielts_speaking.append(IELTS[4])

        # TOEFL
        try:
            TOEFL = " ".join(response.xpath("//*[contains(text(),'TOEFL')]//text()").getall()).split("IELTS")[0]
            TOEFL_list = re.findall(r'\b\d{2,3}\b', TOEFL)
            t_len = len(TOEFL_list)
            TOEFL = [TOEFL_list[0], '', TOEFL_list[1], '' , ''] if t_len == 2 else (
                    [TOEFL_list[0], "", "", "", ""] if t_len == 1 else (["", "", "", "", ""]))
        except:
            TOEFL = ["", "", "", "", ""]
        self.toefl_overall.append(TOEFL[0])
        self.toefl_reading.append(TOEFL[1])
        self.toefl_writing.append(TOEFL[2])
        self.toefl_listening.append(TOEFL[3])
        self.toefl_speaking.append(TOEFL[4])

    def get_currency(self, text):
        currency = re.findall(r'[-+]?\d*\.\d+|\d+', text.replace(',', ''))
        if len(currency) >= 1:
            return currency[0].replace(u'$', '')

