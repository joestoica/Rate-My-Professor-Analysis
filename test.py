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


teacherList = []
tagFeedBackList = []
ratingList = []
takeAgainList = []

class RateMyProfAPI:
    def __init__(self, schoolId = 440, teacher = "staff"):

        global teacherList
        if teacher != "staff":
            teacher = str(teacher).replace(", ", "+")
        else:
            teacher = ""
        self.pageData = ""
        self.finalUrl = ""
        self.tagFeedBack = ""
        self.rating = ""
        self.takeAgain = ""
        self.teacherName = teacher
        self.index = -1

        self.schoolId = schoolId

        try:
            self.index = teacherList.index(self.teacherName)
        except ValueError:
            teacherList.append(self.teacherName)
    
    # Retrieve names ------------------------------------
    def retrieveRMPInfo(self):
        """
        :function: initialize the RMP data
        """

        global tagFeedBackList, ratingList, takeAgainList
        if self.teacherName == "":
            self.rating = INFO_NOT_AVAILABLE
            self.takeAgain = INFO_NOT_AVAILABLE
            self.tagFeedBack = []

            ratingList.append(INFO_NOT_AVAILABLE)
            takeAgainList.append(INFO_NOT_AVAILABLE)
            tagFeedBackList.append(INFO_NOT_AVAILABLE)

            return
    
        # Retrieve names ------------------------------------
        if self.index == -1:
            url = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&" \
                  "queryBy=teacherName&schoolName=Indiana+University&schoolID=%s&query=" % self.schoolId + self.teacherName

            
            page = requests.get(url=url, headers=headers)
            self.pageData = page.text
            pageDataTemp = re.findall(r'ShowRatings\.jsp\?tid=\d+', self.pageData)
            
            if len(pageDataTemp) > 0:
                pageDataTemp = re.findall(r'ShowRatings\.jsp\?tid=\d+', self.pageData)[0]
                self.finalUrl = "https://www.ratemyprofessors.com/" + pageDataTemp
                self.tagFeedBack = []
                # Get tags
                page = requests.get(self.finalUrl)
                t = etree.HTML(page.text)
                tag_labels = str(t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[2]/div[2]/span/text()'))
                scores = str(t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[2]/div[2]/span/b/text()'))
                
                tagList = re.findall(r'\' (.*?) \'', tag_labels)
                score_list = re.findall(r'\'(.*?)\'', scores)
                tags = []
                
                for i, item in enumerate(tagList):
                    tags.append(tagList[i] + " " + score_list[i])
                
                if len(tags) == 0:
                    self.tagFeedBack = []
                else:
                    self.tagFeedBack = tags

                # Get rating
                self.rating = str(t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[1]/div/div[1]/div/div/div/text()'))
                if re.match(r'.*?N/A', self.rating):
                    self.rating = INFO_NOT_AVAILABLE
                else:
                    try:
                        self.rating = re.findall(r'\d\.\d', self.rating)[0]
                    except IndexError:
                        self.rating = INFO_NOT_AVAILABLE

                # Get "Would Take Again" Percentage
                self.takeAgain = str(
                    t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/text()'))
                if re.match(r'.*?N/A', self.takeAgain):
                    self.takeAgain = INFO_NOT_AVAILABLE
                else:
                    try:
                        self.takeAgain = re.findall(r'\d+%', self.takeAgain)[0]
                    except IndexError:
                        self.takeAgain = INFO_NOT_AVAILABLE

            else:
                self.rating = INFO_NOT_AVAILABLE
                self.takeAgain = INFO_NOT_AVAILABLE
                self.tagFeedBack = []

            ratingList.append(self.rating)
            takeAgainList.append(self.takeAgain)
            tagFeedBackList.append(self.tagFeedBack)

        else:
            self.rating = ratingList[self.index]
            self.takeAgain = takeAgainList[self.index]
            self.tagFeedBack = tagFeedBackList[self.index]

    
    # getRMPInfo ------------------------------------
    def getRMPInfo(self):
        """
        :return: RMP rating.
        """

        if self.rating == INFO_NOT_AVAILABLE:
            return INFO_NOT_AVAILABLE

        return self.rating
    
    # Retrieve names ------------------------------------
    
    def getTags(self):
        """

        :return: teacher's tag in [list]
        """
        return self.tagFeedBack
        
    # Retrieve names ------------------------------------
    def getFirstTag(self):
        """

        :return: teacher's most popular tag [string]
        """
        if len(self.tagFeedBack) > 0:
            return self.tagFeedBack[0]

        return INFO_NOT_AVAILABLE
    
    # Retrieve names ------------------------------------
    def getWouldTakeAgain(self):
        """

        :return: teacher's percentage of would take again.
        """
        return self.takeAgain


all_teachers = []

# Retrieve all names ------------------------------------
def retrieve_RMP_names():
        # as of 9/30.19 there are 4264 entries on RMP, so we need 4264/20 iterations
        r = 214
        for i in range(r):
            offset = (i) * 20
            finalUrl = "http://www.ratemyprofessors.com/search.jsp?query=&queryoption=HEADER&stateselect=&country=&dept=&queryBy=teacherName&facetSearch=true&schoolName=indiana+university+bloomington&offset=%s&max=20" % offset
            page = requests.get(finalUrl)
            t = etree.HTML(page.text)
            
            for index in range(20):
                index = index + 1
                teacher = str(t.xpath("/html/body/div[2]/div[4]/div/div/div[2]/ul/li[%s]/a/span[2]/span[1]/text()"%index))
                
                all_teachers.append(teacher[2:-3])

retrieve_RMP_names()

d = []
for i, n in enumerate(all_teachers):
    aapi = RateMyProfAPI(teacher = all_teachers[i])
    aapi.retrieveRMPInfo()
    d.append({'name': all_teachers[i],'tags': aapi.getTags(), 'rmp_info': aapi.getRMPInfo(), 'take_again': aapi.getWouldTakeAgain()})

my_df = pd.DataFrame(d)

my_df.to_csv("~/Documents/life/r/grades/rmp.csv", encoding='utf-8', index=False)
