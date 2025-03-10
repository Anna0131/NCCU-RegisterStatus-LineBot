
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time
import threading

LINE_NOTIFY_TOKEN = 'JbyB0r9U8mA9Rz7dyfaTwJ2dTYy1lkaPDa7QyRgEw5C'

# 已報到名單（初始化為空列表）
reported_people = []

def send_line_notify(message):
    """發送通知到 LINE"""
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"message": message}
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload)
    if response.status_code == 200:
        print("通知發送成功！")
    else:
        print(f"通知發送失敗，HTTP 狀態碼: {response.status_code}")

def fetch_report_status_with_dependencies():
    """使用 Firefox 抓取需要先選招生別後動態加載的系所資料"""
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    driver.get("http://examreg.nccu.edu.tw/Home/Index3")

    try:
        # 選擇「招生別」
        group_dropdown = Select(driver.find_element(By.ID, "regtpe_value"))
        group_dropdown.select_by_visible_text("114碩班甄試")

        # 等待「系所選項」更新
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dep_num"))
        )

        # 選擇「系所」
        department_dropdown = Select(driver.find_element(By.ID, "dep_num"))
        department_dropdown.select_by_visible_text("8621 資訊安全碩士學位學程一般生")

        # 提交表單
        submit_button = driver.find_element(By.ID, "button")
        submit_button.click()

        # 等待結果頁面加載
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Result_List"))
        )

        # 抓取表格內容
        table = driver.find_element(By.XPATH, '//div[@id="Result_List"]/table')
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # 跳過表頭

        report_results = []
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            exam_number = columns[0].text.strip()  # 準考證號碼
            name = columns[1].text.strip()  # 姓名
            rank = columns[3].text.strip()  # 錄取別
            status = columns[4].text.strip()  # 報到結果
            report_results.append({"exam_number": exam_number, "name": name, "rank": rank, "status": status})

        return report_results

    except Exception as e:
        print(f"抓取資料時出錯: {e}")
        return []

    finally:
        driver.quit()
def check_and_notify_new_reports():
    """檢查新報到的同學，並通知包含所有已完成報到人員的統計"""
    global reported_people
    results = fetch_report_status_with_dependencies()
    new_reports = [p for p in results if p['status'] == '報到' and p['name'] != '陳Ｏ璇' and p['name'] != '施Ｏ妤' and p not in reported_people]

    if new_reports:
        # 將新報到的同學加入已報到名單
        reported_people.extend(new_reports)

        # 整合通知訊息
        message = "\n最新報到情況如下：\n"

        # 統計報到人數
        eligible_people = [p for p in reported_people if "正取" in p['rank'] or "備取" in p['rank']]
        reported_count = len(eligible_people)
        max_students = 11  # 招生上限
        message += f"\n總共 {reported_count} 人完成報到。\n"
        if reported_count >= max_students:
            message += "招生名額已滿！\n"
        else:
            message += "尚未滿額，仍有機會錄取。\n"


        for person in reported_people:  # 包含所有已完成報到的同學
            message += f"{person['rank']} {person['name']} 已完成報到！\n"
        

        print(message)
        send_line_notify(message)
    else:
        print("沒有新報到的同學，無需通知。")



def process_now_command():
    """處理 'now' 指令，傳送目前報到狀況到 LINE"""
    global reported_people
    if not reported_people:
        message = "目前沒有已完成報到的同學。"
    else:
        message = "目前已完成報到的人員：\n"
        for person in reported_people:
            message += f"{person['rank']} {person['name']}\n"
    print(message)
    send_line_notify(message)

def monitor_report_status():
    """每 10 分鐘檢查一次報到狀況"""
    while True:
        print("檢查報到狀況中...")
        check_and_notify_new_reports()
        print("等待 10 分鐘後再次檢查...")
        time.sleep(600)  # 每 10 分鐘檢查一次

# 啟動程式
if __name__ == "__main__":
    # 啟動監控報到情況的執行緒
    thread = threading.Thread(target=monitor_report_status)
    thread.start()

    # 處理使用者指令
    while True:
        command = input("請輸入指令（例如 'now'）：").strip().lower()
        if command == "now":
            process_now_command()