import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import random
import json 



def browser_init(isWait):
    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_settings_popups': 0,
        'profile.default_content_setting_values.images': 2
    }
    options.add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome(options=options)
    if isWait:
        browser.implicitly_wait(10)
    return browser

def openPage(browser):
    browser.get("http://search.cnki.com.cn/Search/Result?content=%u4E92%u8054%u7F51%2B%u6559%u80B2")
    time.sleep(0.5)


def collectTitleAndKeyword(browser, papers):
    # cont = browser.find_element_by_class_name('lplist')
    retry_max = 5
    wait = WebDriverWait(browser, 10, 0.5)
    contentLocator = (By.XPATH, "//div[@class='lplist']/div[@class='list-item']")
    try:
        wait.until(EC.presence_of_element_located(contentLocator))
    except:
        print("collectTitleAndKeyword wait list-item time out, failed!")
        return False
    
    cont = browser.find_elements_by_xpath("//div[@class='lplist']/div[@class='list-item']")
    for _, item in enumerate(cont):
        count1 = 0
        flag1 = True
        title = ""
        while flag1 and count1 < retry_max:
            try:
                ti = item.find_element_by_xpath("p[@class='tit clearfix']/a[1]")
                title = ti.get_attribute("title")
                flag1 = False
            except:
                count1 += 1
                time.sleep(1)
        if flag1:
            continue

        if title.find("互联网+") == -1 or title.find("教育") == -1:
            continue

        
        count2 = 0
        flag2 = True
        keywords = []
        while flag2 and count2 < retry_max:
            try:
                keyElement = item.find_element_by_xpath("div[@class='info']/p[@class='info_left left']/a")
                keyStr = keyElement.get_attribute("data-key")
                keywords = keyStr.split('/')
                flag2 = False
            except:
                count2 += 1
                time.sleep(1)
        if flag2:
            continue


        # keyElement = item.find_element_by_xpath("div[@class='info']/p[@class='info_left left']/a")
        # keyStr = keyElement.get_attribute("data-key")
        # keywords = keyStr.split('/')

        print("title:", title)
        print("keywords:", keywords)

        papers[title] = keywords
    
    return True

lastPage = ''

def switchNextPage(browser):
    global lastPage
    wait = WebDriverWait(browser, 10, 0.5)
    pageLocator = (By.XPATH, "//div[@class='page']//a[text()='下一页>']")
    try:
        wait.until(EC.presence_of_element_located(pageLocator))
    except:
        print("switchNextPage failed!")
        return False

    nextPageElement = browser.find_element_by_xpath("//div[@class='page']//a[text()='下一页>']")
    if nextPageElement:
        nextPage = nextPageElement.get_attribute('onclick')
        if lastPage == nextPage:
            print("No next page, finish!")
            return False
        else:
            lastPage = nextPage
            nextPageElement.click()
            return True
    else:
        print("Switch to next page failed!")
        return False
    



if __name__ == "__main__":
    #1、初始化
    browser = browser_init(True)
    openPage(browser)
    papers = {}
    collectTitleAndKeyword(browser, papers)
    time.sleep(2)
    
    #2、翻页，批量选取链接
    while switchNextPage(browser):
        delay = 2+random.random()
        time.sleep(delay)
        if not collectTitleAndKeyword(browser, papers):
            break
        time.sleep(delay)
        
    browser.quit()
    print("采集了%d条数据"% len(papers))

    #3、写入json中
    with open("./stat.json", "w", encoding='utf-8') as j:
        json.dump(papers, j, ensure_ascii=False)
        print("写入json文件完成")
