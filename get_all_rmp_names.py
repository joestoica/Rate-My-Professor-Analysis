import re, requests
from lxml import etree
import logging
import pandas as pd
import numpy as np

#Author Email: yiyangl6@asu.edu
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

INFO_NOT_AVAILABLE = "NA"

all_teachers = []
tagFeedBackList = []
ratingList = []
takeAgainList = []

class RateMyProfAPI:
    
    def __init__(self, schoolId = 440):

        self.index = -1
        self.schoolId = schoolId

    def retrieve_RMP_names(self):

        if self.index == -1:
            for i in range(1):
                offset = (i) * 20
                self.finalUrl = "http://www.ratemyprofessors.com/search.jsp?query=&queryoption=HEADER&stateselect=&country=&dept=&queryBy=teacherName&facetSearch=true&schoolName=indiana+university+bloomington&offset=%s&max=20" % offset
                page = requests.get(self.finalUrl)
                t = etree.HTML(page.text)
                
                for index in range(20):
                    index = index + 1
                    teacher = str(t.xpath("/html/body/div[2]/div[4]/div/div/div[2]/ul/li[%s]/a/span[2]/span[1]/text()"%index))
                    
                    all_teachers.append(teacher[2:-3])
                    

aapi = RateMyProfAPI()
aapi.retrieve_RMP_names()
print(list(filter(None, all_teachers)))


