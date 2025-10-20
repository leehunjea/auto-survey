from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random
from config import *

def generate_random_responses():
    """가중치 기반으로 매 회차 랜덤 응답 생성"""
    responses = {}
    for q_num, weights in RESPONSE_WEIGHTS.items():
        options = list(weights.keys())
        weight_values = list(weights.values())
        responses[q_num] = random.choices(options, weights=weight_values, k=1)[0]
    return responses

def click_checkbox(driver, wait, q_num, option_idx):
    """체크박스 클릭"""
    checkbox_id = f"nsv-survey-question-{q_num}-item-{option_idx}"
    try:
        checkbox = wait.until(EC.presence_of_element_located((By.ID, checkbox_id)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(0.3)
        return checkbox.is_selected()
    except:
        return False

def submit_survey(driver, wait):
    """설문 제출"""
    try:
        wait.until(EC.presence_of_element_located((By.ID, "nsv-survey-question-2-item-0")))
        time.sleep(PAGE_LOAD_WAIT)
        
        responses = generate_random_responses()
        for q_num, option_idx in responses.items():
            click_checkbox(driver, wait, q_num, option_idx)
        
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            if '제출' in btn.text:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(3)
                return True
        return False
    except:
        return False

def click_retry_button(driver):
    """'설문 추가 참여' 버튼 클릭"""
    try:
        time.sleep(2)
        for elem in driver.find_elements(By.XPATH, "//button | //a"):
            if '추가 참여' in elem.text or '추가참여' in elem.text:
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(3)
                return True
        return False
    except:
        return False

def automate_survey_loop():
    """설문 자동화 무한 루프"""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔄 설문 자동화 시작 (랜덤 비율 적용)")
        print(f"   🎯 목표: {MAX_COUNT}회" if MAX_COUNT else "   ♾️  무한 반복 (Ctrl+C 중단)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        driver.get(SURVEY_URL)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        
        count = 0
        success_count = 0
        
        while True:
            count += 1
            print(f"📋 [{count}회차] 진행 중... (성공: {success_count})", end=" ")
            
            if submit_survey(driver, wait):
                success_count += 1
                print("✅")
                
                if MAX_COUNT and success_count >= MAX_COUNT:
                    print(f"\n🎉 목표 {MAX_COUNT}회 달성!")
                    break
                
                if not click_retry_button(driver):
                    driver.refresh()
                    time.sleep(4)
                else:
                    time.sleep(random.randint(NEXT_SURVEY_WAIT_MIN, NEXT_SURVEY_WAIT_MAX))
            else:
                print("✗ 실패")
                driver.refresh()
                time.sleep(4)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 중단됨 - 총 {success_count}회 성공")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
    finally:
        driver.quit()
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🏁 종료 - 성공: {success_count}/{count}회 ({success_count/count*100:.1f}%)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    automate_survey_loop()
