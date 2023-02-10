from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time
import random
import json
import csv


# 设置谷歌驱动器的环境
options = webdriver.ChromeOptions()
# 设置chrome不加载图片，提高速度
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
# 创建一个谷歌驱动器
browser = webdriver.Chrome(options=options)
url = 'https://www.cnki.net/'

# 声明一个全局列表，用来存储字典
data_list = []


def start_spider(key,page):
    
    # 请求url
    browser.get(url)
    # 显示等待输入框是否加载完成
    WebDriverWait(browser, 1000).until(
        EC.presence_of_all_elements_located(
            (By.ID, 'txt_SearchText')
        )
    )
    # 找到输入框的id，并输入python关键字
    browser.find_element(By.ID,'txt_SearchText').click()
    browser.find_element(By.ID,'txt_SearchText').send_keys(key)
    # 输入关键字之后点击搜索
    browser.find_element(By.CLASS_NAME,'search-btn').click()
    # print(browser.page_source)
    # 显示等待文献是否加载完成
    WebDriverWait(browser, 1000).until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'search-result')
        )
    )

    # 声明一个标记，用来标记翻页几页
    count = 1
    while True:
        # 显示等待加载更多按钮加载完成
        WebDriverWait(browser, 1000).until(
            EC.presence_of_all_elements_located(
                (By.ID, 'Page_next_top')
            )
        )
        # 获取加载更多按钮
        Btn = browser.find_element(By.ID, 'Page_next_top')
        # 显示等待该信息加载完成
        WebDriverWait(browser, 1000).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//tbody/tr')
            )
        )

        trs = browser.find_elements(By.XPATH,'//tbody/tr')
        # 遍历循环
        for tr in trs:
            # 获取作者
            author = tr.find_element(By.XPATH,"./td[@class='author']").text
            
            # 文献链接
            link = tr.find_element(By.CLASS_NAME,'fz14').get_attribute('href')
            # 拼接
            link = urljoin(browser.current_url, link)
            # 获取关键字（需要访问该文献，url就是上面获取到的link）
            js = 'window.open("%s");' % link
            # 每次访问链接的时候适当延迟
            time.sleep(random.uniform(1, 2))
            browser.execute_script(js)
           
            browser.switch_to.window(browser.window_handles[1])
            # 获取关键字（使用xpath）
            key_worlds = browser.find_elements(By.XPATH,'//p[@class="keywords"]/a')
            key_worlds = (','.join(map(lambda x: x.text, key_worlds))).replace(';','')
                
                      
            # 获取文献的摘要
            name = browser.find_element(By.CSS_SELECTOR, ".wx-tit > h1").text

            # 获取信息完之后先关闭当前窗口再切换句柄到原先的窗口
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            
            # 声明一个字典存储数据
            data_dict = {}
            data_dict['标题'] = name
            data_dict['作者'] = author
            data_dict['关键字'] = key_worlds

            data_list.append(data_dict)
            print(data_dict)
        # 如果Btn按钮（就是加载更多这个按钮）没有找到（就是已经到底了），就退出
        
        # 如果到了爬取的页数就退出
        if count == page:
            break
        else:
            Btn.click()
        count += 1

        # 延迟两秒，我们不是在攻击服务器
        time.sleep(2)
    # 全部爬取结束后退出浏览器
    browser.quit()


def main():
    x = input('请输入要搜索的关键词：')
    y = input('请输入要爬取的页数：')
    start_spider(x,eval(y))

    # 将数据写入json文件中
    with open('cnki.json', 'a+', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)
    print('json文件写入完成')

    # 将数据写入csv文件
    with open('cnki.csv', 'w', encoding='utf-8', newline='') as f:
        # 表头
        title = data_list[0].keys()
        # 声明writer对象
        writer = csv.DictWriter(f, title)
        # 写入表头
        writer.writeheader()
        # 批量写入数据
        writer.writerows(data_list)
    print('csv文件写入完成')


if __name__ == '__main__':

main()
