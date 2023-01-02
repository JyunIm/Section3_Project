import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

browser = webdriver.Chrome()
nav_list = []
for i in range(3):
    nav_url = f'https://search.shopping.naver.com/search/all?frm=NVSHTTL&origQuery=%EB%B0%80%ED%82%A4%ED%8A%B8&pagingIndex={i}&pagingSize=40&productSet=total&query=%EB%B0%80%ED%82%A4%ED%8A%B8&sort=rel&timestamp=&viewType=list'
    browser.get(nav_url)
    time.sleep(1)

    # 스크롤 내리기
    browser.execute_script('window.scrollTo(0,3000)')
    browser.execute_script('window.scrollTo(0,3000)')
    browser.execute_script('window.scrollTo(0,3000)')

    # 스크래핑
    nav_soup = BeautifulSoup(browser.page_source, 'html.parser')
    nav_items = nav_soup.find_all('div', attrs={'class':'basicList_info_area__TWvzp'})
    # for nav_item in nav_items:
    #     nav_name = nav_item.find('a', attrs={'target':'_blank', 'class':'basicList_link__JLQJf'}).get_text()
    #     nav_price = nav_item.find('span', attrs={'class':'price_num__S2p_v','data-testid':'SEARCH_PRODUCT_PRICE'}).get_text()
    #     nav_fare = nav_item.find('span', attrs={'class':'price_delivery__yw_We'})
    #     if nav_fare:
    #         nav_fare = nav_fare.get_text()
    #     else:
    #         pass
    #     nav_cate = nav_item.find('div',attrs={'class':'basicList_depth__SbZWF'}).get_text()
    #     nav_etc = nav_item.find_all('a', attrs={'class':'basicList_etc__LSkN_'})
    #     for i in range(len(nav_etc)):
    #         if nav_etc[i]:
    #             nav_etc[i] = nav_etc[i].get_text()
    #         else :
    #             pass
    #     nav_etc = ' '.join(nav_etc)
    #     a = {'name' : nav_name, 'price':nav_price,'fare':nav_fare,'category':nav_cate,'etc':nav_etc}
    #     nav_list.append(a)
    #     time.sleep(1)
    time.sleep(2)

