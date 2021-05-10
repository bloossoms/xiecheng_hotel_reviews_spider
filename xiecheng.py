# 准备工作：selenium,Chrome浏览器,ChromeDriver,pyquery 安装和配置
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import csv
import time
import random
import os
# import pandas as pd
options = webdriver.ChromeOptions()
options.add_argument("disable-blink-features=AutomationControlled") # 去掉webdriver痕迹
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser,100)

###############参数设置############################
hotel_code = 1  #酒店起始编号
MAX_PAGE = 1000  #评论页上限
comment_page_nums = MAX_PAGE  #剩余需爬取页数
save_dir_csv = 'data-beijing-csv' # 保存文件夹
# save_dir_xlsx = 'data-beijing' # 保存文件夹
hotel_score_file = save_dir_csv+'/hotel_scores_xiecheng.csv'
# 酒店id  用于构造链接
hotels = [
    '793504',
    '1251776',
    '1726454',
    '2042738',
    '429044',
    '667157',
    '429531',
    '427151',
    '374791',
    '2298855',
    '375126',
    '6492450',
    '11305146',
    '1776800',
    '25748541',
    '763434',
    '608516',
    '431617',
    '457112',
    '32808664',
    '9627725',
    '2043832',
    '485588',
    '1466503',
    '7008186',
    '1013461',
    '1881966',
    '447443',
    '2612318',
    '748929',
    '1212045',
    '2383782',
    '856467',
    '472933',
    '1419816',
    '454138',
    '1641789',
    '632424',
    '8105721',
    '8911756',
    '760206',
    '1736509',
    '6728863',
    '835618',
    '927955',
    '1947567',
    '1606836',
    '25825681',
    '429527',
    '2239073',
    '9557111',
    '793933',
    '975443',
    '28707025',
    '2299691',
    '486026',
    '1641681',
    '1064097',
    '2298378',
    '53887811',
    '43666615',
    '855375',
    '434454',
    '14284387',
    '1452169',
    '2239929',
    '1775747',
    '660934',
    '1379329',
    '13798999',
    '812621',
    '790534',
    '474107',
    '468772',
    '2302512',
    '760201',
    '8626494',
    '8626494',
    '9667001',
    '1107145',
    '427531',
    '1736507',
    '436167',
    '9558031',
    '1537661',
    '910943',
    '1733899',
    '1055636',
    '13180770',
    '821582',
    '347310',
    '5950980',
    '431407',
    '430004',
    '1521182',
    '2220151',
    '706607',
    '841915',
    '42712501',
    '2018295'
]



def index_page(url):
    '''
    打开初试页面，爬取第一页数据，然后进入后续页数爬取循环
    :param url: 初试页面链接
    :return: 无
    '''
    try:
        global comment_page_nums,browser
        browser.get(url)
        print(url)
        page = 1
        all = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.detail-headreview_all')))
        all.click()
        comment_page_nums = comment_page_nums - 1
        time.sleep(2)
        click_all = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.m-fastfilter button:first-child')))
        click_all.click()
        time.sleep(3)
        get_total_page()
        get_score()
        get_comment()
        time.sleep(2)
        while (comment_page_nums):
            comment_page_nums = comment_page_nums - 1
            page = page + 1
            next = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-pagination_item .forward')))
            next.click()
            time.sleep(random.randint(2, 4))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-reviewCard-item')))
            wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.m_num_checked'), str(page)))
            get_comment()
            time.sleep(1)
    except TimeoutException as e:
        print(e.args)
    # finally:
    #     csv_to_xlsx_pd('/hotel_scores_xiecheng')


def get_total_page():
    '''
    获取评论总页数
    :return: 无
    '''
    global comment_page_nums
    html = browser.page_source
    doc = pq(html)
    page_bar = doc('.m-pagination_numbers div')
    nums = []
    for page in page_bar.items():
        num = page.text()
        nums.append(num)
    num = int(nums.pop())
    if num < comment_page_nums:
        comment_page_nums = num - 1
    print('此酒店共',num,'页评论！')


def get_score():
    '''
    获取酒店各项评分
    :return: 无
    '''
    html = browser.page_source
    doc = pq(html)
    scores = doc('.m-reviewScore_single li')
    res = []
    for li in scores.items():
        score = li.find('.score').text()
        res.append(score)

    hotel =  {
        "酒店名称": 'H'+str(hotel_code_encoded),
        "酒店真名":doc.find('.detail-headline_title h1').text(),
        "总分": doc.find('.detail-headreview_score_box b').text(),
        "环境得分": res[0],
        "卫生得分": res[1],
        "服务得分": res[2],
        "设施得分": res[3],
        "评论总数": comment_page_nums+1
    }
    print(hotel)
    save_hotels(hotel)

def get_comment():
    '''
    获取酒店评论
    :return: 无
    '''
    global hotel_code
    html = browser.page_source
    doc = pq(html)
    name = doc.find('.detail-headline_title h1').text()
    comment = {}
    comment_lists = doc('.smart-modal_container .m-module-bg .list .m-reviewCard-item').items()
    for comment_list in comment_lists:
        comment = {
            "酒店名称": 'H' + str(hotel_code_encoded),
            "酒店真名": name,
            '用户名':comment_list.find('p.name').text(),
            '个人评分': comment_list.find('.m-score_single strong').text(),
            '评论日期': comment_list.find('.comment .reviewDate').text(),
            '评论详情':comment_list.find('.comment p').text()
        }
        save_comments(comment)

def save_hotels(hotel):
    '''
    保存酒店评分
    :param hotel: 酒店评分信息
    :return: 无
    '''
    with open(hotel_score_file,'a',newline='',encoding='gb18030') as csvfile:
        fieldnames = ['酒店名称','酒店真名','总分','环境得分','卫生得分','服务得分','设施得分','评论总数']
        writer = csv.DictWriter(csvfile,fieldnames = fieldnames)
        writer.writerow(hotel)

def save_comments(comment):
    '''
    保存酒店评论信息到 hotel_comments_H01.csv...
    :param comment: 酒店评论
    :return:
    '''
    with open(hotel_comment_file,'a',newline='',encoding='gb18030') as csvfile:
        fieldnames = ['酒店名称','酒店真名','用户名','个人评分','评论日期','评论详情']
        writer = csv.DictWriter(csvfile,fieldnames = fieldnames)
        writer.writerow(comment)
        print(comment)

# def csv_to_xlsx_pd(file_name): #将csv转xlsx
#     csv = pd.read_csv(save_dir_csv+file_name + '.csv', encoding='gb18030')
#     csv.to_excel(save_dir_xlsx+file_name + '.xlsx', index = False)

if __name__ == '__main__':

    # 初始化保存酒店评分信息文件 hotel_scores_xiecheng.csv
    if not os.path.exists(hotel_score_file):
        with open(hotel_score_file, 'w', newline='', encoding='gb18030') as csvfile:
            fieldnames = ['酒店名称', '酒店真名', '总分', '环境得分', '卫生得分', '服务得分', '设施得分','评论总数']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    # 遍历各个酒店id，爬取其网页上评论
    for hotel_id in hotels:
        hotel_code_encoded = str(hotel_code).rjust(2, '0')# 酒店编码统一成两位数（100以内）
        file_name = '/hotel_comments_H{0}'.format(hotel_code_encoded)
        hotel_comment_file = save_dir_csv+'/hotel_comments_H{0}.csv'.format(hotel_code_encoded)
        # 初始化各酒店评论保存文件
        with open(hotel_comment_file, 'w', newline='', encoding='gb18030') as csvfile:
            fieldnames = ['酒店名称', '酒店真名','用户名', '个人评分', '评论日期','评论详情']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
        url = 'https://hotels.ctrip.com/hotels/' + hotel_id + '.html'
        index_page(url)
        comment_page_nums = MAX_PAGE
        hotel_code += 1
    browser.close()
