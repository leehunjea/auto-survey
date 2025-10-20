import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QSpinBox, QComboBox, QTextEdit, QProgressBar,
                              QGroupBox, QFormLayout, QSlider, QCheckBox,
                              QScrollArea, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random


class QuestionSettingWidget(QWidget):
    """개별 질문 설정 위젯"""
    def __init__(self, question_num, parent=None):
        super().__init__(parent)
        self.question_num = question_num
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 질문 헤더
        header = QLabel(f"질문 {self.question_num}")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        layout.addWidget(header)
        
        # 질문 타입 선택
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("질문 타입:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["객관식", "주관식"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # 객관식 설정 (초기 표시)
        self.multiple_choice_widget = QWidget()
        mc_layout = QVBoxLayout()
        
        # 옵션 개수
        option_count_layout = QHBoxLayout()
        option_count_layout.addWidget(QLabel("옵션 개수:"))
        self.option_count_spin = QSpinBox()
        self.option_count_spin.setRange(2, 10)
        self.option_count_spin.setValue(4)
        self.option_count_spin.valueChanged.connect(self.update_option_sliders)
        option_count_layout.addWidget(self.option_count_spin)
        option_count_layout.addStretch()
        mc_layout.addLayout(option_count_layout)
        
        # 옵션별 비율 슬라이더
        self.sliders_widget = QWidget()
        self.sliders_layout = QVBoxLayout()
        self.sliders_widget.setLayout(self.sliders_layout)
        self.option_sliders = []
        self.option_labels = []
        
        mc_layout.addWidget(self.sliders_widget)
        self.multiple_choice_widget.setLayout(mc_layout)
        layout.addWidget(self.multiple_choice_widget)
        
        # 주관식 설정 (초기 숨김)
        self.text_widget = QWidget()
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("응답 텍스트 목록 (한 줄에 하나씩):"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("AI 기반 서비스를 기대합니다.\n편리할 것 같습니다.\n좋은 아이디어입니다.")
        self.text_input.setMaximumHeight(100)
        text_layout.addWidget(self.text_input)
        self.text_widget.setLayout(text_layout)
        self.text_widget.hide()
        layout.addWidget(self.text_widget)
        
        # 초기 슬라이더 생성
        self.update_option_sliders()
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)
    
    def on_type_changed(self, index):
        """질문 타입 변경 시"""
        if index == 0:  # 객관식
            self.multiple_choice_widget.show()
            self.text_widget.hide()
        else:  # 주관식
            self.multiple_choice_widget.hide()
            self.text_widget.show()
    
    def update_option_sliders(self):
        """옵션 슬라이더 업데이트"""
        # 기존 슬라이더 안전하게 제거
        while self.sliders_layout.count():
            item = self.sliders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.option_sliders.clear()
        self.option_labels.clear()
        
        # 새 슬라이더 생성
        count = self.option_count_spin.value()
        default_value = 100 // count
        
        for i in range(count):
            option_layout = QHBoxLayout()
            option_layout.addWidget(QLabel(f"옵션 {i+1}:"))
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(default_value)
            
            label = QLabel(f"{default_value}%")
            label.setMinimumWidth(50)
            
            slider.valueChanged.connect(lambda v, lbl=label: lbl.setText(f"{v}%"))
            
            option_layout.addWidget(slider)
            option_layout.addWidget(label)
            
            self.option_sliders.append(slider)
            self.option_labels.append(label)
            
            widget = QWidget()
            widget.setLayout(option_layout)
            self.sliders_layout.addWidget(widget)
    
    def get_config(self):
        """설정 가져오기"""
        if self.type_combo.currentIndex() == 0:  # 객관식
            weights = {}
            for i, slider in enumerate(self.option_sliders):
                weights[i] = slider.value()
            return {'type': 'multiple', 'weights': weights}
        else:  # 주관식
            texts = [t.strip() for t in self.text_input.toPlainText().split('\n') if t.strip()]
            return {'type': 'text', 'texts': texts or ['기본 응답입니다.']}


class SurveyWorker(QThread):
    """설문 자동화 작업 스레드"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int, int)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True
    
    def run(self):
        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.get(self.config['url'])
            wait = WebDriverWait(driver, 60)
            
            count = 0
            success = 0
            max_count = self.config['max_count']
            
            while self.running and (max_count == 0 or success < max_count):
                count += 1
                self.progress.emit(f"[{count}회차] 시작...")
                
                if self.submit_survey(driver, wait):
                    success += 1
                    self.progress.emit(f"✅ [{count}회차] 성공! (누적: {success})")
                    
                    if not self.click_retry(driver):
                        driver.refresh()
                        time.sleep(3)
                    time.sleep(random.randint(2, 4))
                else:
                    self.progress.emit(f"✗ [{count}회차] 실패")
                    driver.refresh()
                    time.sleep(3)
            
            driver.quit()
            self.finished.emit(success, count)
            
        except Exception as e:
            self.progress.emit(f"❌ 오류: {str(e)}")
            self.finished.emit(0, 0)
    
    def submit_survey(self, driver, wait):
        try:
            wait.until(EC.presence_of_element_located((By.ID, "nsv-survey-question-2-item-0")))
            time.sleep(4)
            
            # 각 질문 처리
            for q_num, q_config in self.config['questions'].items():
                if q_config['type'] == 'multiple':
                    # 객관식
                    weights = q_config['weights']
                    if weights:
                        option = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
                        checkbox_id = f"nsv-survey-question-{q_num}-item-{option}"
                        try:
                            checkbox = driver.find_element(By.ID, checkbox_id)
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(0.3)
                            driver.execute_script("arguments[0].click();", checkbox)
                            time.sleep(0.3)
                        except:
                            pass
                else:
                    # 주관식
                    try:
                        textarea = driver.find_element(By.XPATH, "//textarea")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
                        time.sleep(0.3)
                        textarea.clear()
                        textarea.send_keys(random.choice(q_config['texts']))
                    except:
                        pass
            
            # 제출
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
    
    def click_retry(self, driver):
        try:
            time.sleep(2)
            for elem in driver.find_elements(By.XPATH, "//button | //a"):
                if '추가 참여' in elem.text:
                    driver.execute_script("arguments[0].click();", elem)
                    time.sleep(3)
                    return True
        except:
            pass
        return False
    
    def stop(self):
        self.running = False


class SurveyBotAdvancedGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.question_widgets = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('네이버 폼 자동화 봇 v2.0 - 고급 설정')
        self.setGeometry(100, 100, 900, 800)
        
        # 메인 위젯
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # 탭 위젯
        tabs = QTabWidget()
        
        # === 탭 1: 기본 설정 ===
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        
        # URL 설정
        url_group = QGroupBox("📋 기본 설정")
        url_layout = QFormLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://form.naver.com/response/...")
        url_layout.addRow("설문 URL:", self.url_input)
        
        self.max_count_input = QSpinBox()
        self.max_count_input.setRange(0, 10000)
        self.max_count_input.setValue(100)
        self.max_count_input.setSpecialValueText("무한 반복")
        url_layout.addRow("제출 목표:", self.max_count_input)
        
        self.question_count_input = QSpinBox()
        self.question_count_input.setRange(1, 50)
        self.question_count_input.setValue(13)
        self.question_count_input.valueChanged.connect(self.update_question_tabs)
        url_layout.addRow("질문 개수:", self.question_count_input)
        
        url_group.setLayout(url_layout)
        basic_layout.addWidget(url_group)
        
        # 빠른 설정 버튼
        quick_layout = QHBoxLayout()
        
        load_btn = QPushButton("📂 설정 불러오기")
        load_btn.clicked.connect(self.load_config)
        quick_layout.addWidget(load_btn)
        
        save_btn = QPushButton("💾 설정 저장하기")
        save_btn.clicked.connect(self.save_config)
        quick_layout.addWidget(save_btn)
        
        basic_layout.addLayout(quick_layout)
        basic_layout.addStretch()
        
        basic_tab.setLayout(basic_layout)
        tabs.addTab(basic_tab, "⚙️ 기본 설정")
        
        # === 탭 2: 질문 설정 ===
        questions_tab = QWidget()
        questions_layout = QVBoxLayout()
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.questions_layout = QVBoxLayout()
        scroll_widget.setLayout(self.questions_layout)
        scroll.setWidget(scroll_widget)
        
        questions_layout.addWidget(scroll)
        questions_tab.setLayout(questions_layout)
        tabs.addTab(questions_tab, "❓ 질문별 설정")
        
        # === 탭 3: 실행 ===
        run_tab = QWidget()
        run_layout = QVBoxLayout()
        
        # 실행 버튼
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ 시작")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_automation)
        
        self.stop_button = QPushButton("⏹ 중지")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_button.clicked.connect(self.stop_automation)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        run_layout.addLayout(button_layout)
        
        # 로그
        log_group = QGroupBox("📊 실행 로그")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: Consolas, monospace;
            font-size: 12px;
            padding: 10px;
        """)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        run_layout.addWidget(log_group)
        
        run_tab.setLayout(run_layout)
        tabs.addTab(run_tab, "🚀 실행")
        
        layout.addWidget(tabs)
        main_widget.setLayout(layout)
        
        # 초기 질문 위젯 생성
        self.update_question_tabs()
    
    def update_question_tabs(self):
        """질문 위젯 업데이트 (에러 수정 버전)"""
        # 기존 위젯 안전하게 제거
        while self.questions_layout.count():
            item = self.questions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.question_widgets.clear()
        
        # 새 위젯 생성 (질문 번호는 2부터 시작 - 네이버 폼 구조)
        count = self.question_count_input.value()
        for i in range(count):
            q_num = i + 2  # 실제 질문 번호
            widget = QuestionSettingWidget(q_num - 1)  # 표시는 1부터
            self.question_widgets[q_num] = widget
            self.questions_layout.addWidget(widget)
        
        self.questions_layout.addStretch()
    
    def start_automation(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "설문 URL을 입력하세요!")
            return
        
        # 설정 수집
        config = {
            'url': url,
            'max_count': self.max_count_input.value(),
            'questions': {}
        }
        
        for q_num, widget in self.question_widgets.items():
            config['questions'][q_num] = widget.get_config()
        
        self.add_log("🚀 자동화 시작!")
        self.add_log(f"📝 URL: {url}")
        self.add_log(f"🎯 목표: {config['max_count']}회\n")
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.worker = SurveyWorker(config)
        self.worker.progress.connect(self.add_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def stop_automation(self):
        if self.worker:
            self.worker.stop()
            self.add_log("⏹ 중지 요청됨...")
    
    def on_finished(self, success, total):
        self.add_log(f"\n🎉 완료! 성공: {success}/{total}회")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def add_log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def save_config(self):
        """설정 저장"""
        config = {
            'url': self.url_input.text(),
            'max_count': self.max_count_input.value(),
            'question_count': self.question_count_input.value(),
            'questions': {}
        }
        
        for q_num, widget in self.question_widgets.items():
            config['questions'][str(q_num)] = widget.get_config()
        
        try:
            with open('survey_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "성공", "설정이 survey_config.json에 저장되었습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패: {e}")
    
    def load_config(self):
        """설정 불러오기"""
        try:
            with open('survey_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.url_input.setText(config.get('url', ''))
            self.max_count_input.setValue(config.get('max_count', 100))
            self.question_count_input.setValue(config.get('question_count', 13))
            
            QMessageBox.information(self, "성공", "기본 설정이 불러와졌습니다!")
        except FileNotFoundError:
            QMessageBox.warning(self, "경고", "survey_config.json 파일이 없습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"불러오기 실패: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SurveyBotAdvancedGUI()
    window.show()
    sys.exit(app.exec_())
