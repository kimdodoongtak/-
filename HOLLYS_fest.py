#!/usr/bin/env python
# coding: utf-8

# In[6]:


import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook

# 크롬 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# 크롬 드라이버 경로 지정
driver_path = ''
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 타겟 네이버 플레이스 URL 설정
target_url = 'https://m.place.naver.com/restaurant/1052747813/review/visitor?entry=pll&reviewSort=recent'

# 결과 저장용 워크북
now = datetime.datetime.now()
xlsx = Workbook()
list_sheet = xlsx.create_sheet('output')
list_sheet.append(['nickname', 'content', 'date', 'tag_text', 'url'])

try:
    driver.get(target_url)

    # 리뷰 박스 로딩 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.place_apply_pui.EjjAW'))
        )
        print("리뷰 목록 로딩 완료!")
    except TimeoutException:
        print("리뷰 목록이 로딩되지 않음")
        driver.quit()
        exit()

    time.sleep(1)

    # 더보기 클릭 반복 → 2023년 등장 시 중단
    while True:
        # 현재 페이지 리뷰 요소 수집
        reviews = driver.find_elements(By.CSS_SELECTOR, 'li.place_apply_pui.EjjAW')
        stop_loading = False  # 2023년 이하 발견 여부

        for review in reviews:
            try:
                blind_spans = review.find_elements(By.CSS_SELECTOR, 'span.pui__blind')
                for span in blind_spans:
                    if '년' in span.text and '월' in span.text:
                        date = span.text.strip()
                        break
                else:
                    continue  # 날짜 못 찾으면 패스

                if date.startswith("2023") or date.startswith("2022"):
                    print(f"{date} → 더 이상 수집하지 않음")
                    stop_loading = True
                    break
            except Exception as e:
                print("날짜 확인 중 오류:", e)
                continue

        if stop_loading:
            break

        # 더보기 버튼 클릭
        try:
            more_button = driver.find_element(By.CSS_SELECTOR, 'a.fvwqf')
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(1.5)
        except NoSuchElementException:
            print("더 이상 누를 더보기 버튼이 없습니다")
            break
        except ElementClickInterceptedException:
            print("클릭이 막혔습니다")
            time.sleep(1)

    # 최종 리뷰 크롤링
    reviews = driver.find_elements(By.CSS_SELECTOR, 'li.place_apply_pui.EjjAW')

    for review in reviews:
        try:
            date = ''
            blind_spans = review.find_elements(By.CSS_SELECTOR, 'span.pui__blind')
            for span in blind_spans:
                if '년' in span.text and '월' in span.text:
                    date = span.text.strip()
                    break

            if date.startswith("2025"):
                continue  # 건너뜀
            elif date.startswith("2024"):
                nickname = review.find_element(By.CSS_SELECTOR, 'span.pui__NMi-Dp').text
                content = review.find_element(By.CSS_SELECTOR, 'div.pui__vn15t2 > a').text

                tag_elements = review.find_elements(By.CSS_SELECTOR, 'div.pui__HLNvmI > span.pui__jhpEyP')
                tags = [tag.text.strip() for tag in tag_elements]
                tag_text = ', '.join(tags)

                list_sheet.append([nickname, content, date, tag_text, target_url])
            else:
                print(f"{date}는 수집 대상이 아님")
                break

        except Exception as e:
            print("리뷰 추출 중 오류:", e)
            continue

finally:
    # Excel 저장 및 종료
    file_name = f'naver_review_{now.strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
    xlsx.save(file_name)
    driver.quit()
    print(f"Data collection completed and saved to Excel → {file_name}")


# In[ ]:




