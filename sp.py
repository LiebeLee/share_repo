import os
import time
from selenium import webdriver
import json


def browser_init(isWait):
    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_settings_popups': 0,
        'profile.default_content_setting_values.images': 2
    }
    options.add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome()
    if isWait:
        browser.implicitly_wait(10)
    return browser

def openPage(browser):
    browser.get("http://search.cnki.com.cn/Search/Result?content=%u4E92%u8054%u7F51%2B%u6559%u80B2")
    time.sleep(0.5)


def collectTitleAndKeyword(browser, papers):
    # cont = browser.find_element_by_class_name('lplist')
    cont = browser.find_elements_by_xpath("//div[@class='lplist']/div[@class='list-item']")
    for _, item in enumerate(cont):
        ti = item.find_element_by_xpath("p[@class='tit clearfix']/a[1]")
        title = ti.get_attribute("title")
        # print("titile:", title)

        if title.find("互联网+") == -1 or title.find("教育") == -1:
            continue

        keyInfo = item.find_element_by_xpath("div[@class='info']/p[@class='info_left left']")
        keyElement = keyInfo.find_element_by_xpath("a[1]")
        keyStr = keyElement.get_attribute("data-key")
        keywords = keyStr.split('/')
        # print("keywords:", keywords)

        papers[title] = keywords


def switchNextPage(browser):
    page = browser.find_element_by_xpath("//div[@class='page']")
    nextPage = page.find_element_by_xpath("a[text()='下一页>']")
    if nextPage:
        nextPage.click()
        return True
    else:
        return False

    # //*[@id="PageContent"]/div[1]/div[2]/div[13]/a[11]
    



if __name__ == "__main__":
    #1、初始化
    browser = browser_init(True)
    openPage(browser)
    papers = {}
    collectTitleAndKeyword(browser, papers)

    #2、翻页，批量选取链接
    # while switchNextPage(browser):
    #     time.sleep(0.1)
    #     collectTitleAndKeyword(browser, papers)
    #     time.sleep(1)
        
    browser.quit()
    print("采集了%d条数据"% len(papers))

    #3、写入json中
    with open("./stat.json", "w", encoding='utf-8') as j:
        json.dump(papers, j, ensure_ascii=False)
        print("写入json文件完成")
