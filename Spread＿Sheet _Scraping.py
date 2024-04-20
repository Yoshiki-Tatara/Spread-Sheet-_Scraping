from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import smtplib
from email.mime.text import MIMEText

# Googleスプレッドシートの設定
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('your_credentials_file.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Your Spreadsheet Name").sheet1

# Seleniumの設定
options = Options()
options.add_argument("user-agent=Your User Agent String")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# スプレッドシートからURLリストを取得
urls = sheet.col_values(1)  # A列

for url in urls:
    driver.get(url)
    time.sleep(5)  # ページが完全にロードされるまで待つ

    # 在庫情報を確認するロジック（サイトによって異なります）
    stock_status = driver.find_element(By.CSS_SELECTOR, "your_css_selector_for_stock_info").text

    if "在庫あり" in stock_status:  # 在庫状況に応じて調整
        # Gmailで通知
        content = f"在庫あり: {url}"
        msg = MIMEText(content)
        msg['Subject'] = '在庫通知'
        msg['From'] = 'your_email@gmail.com'
        msg['To'] = 'recipient_email@gmail.com'

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login('your_email@gmail.com', 'your_password')
        server.send_message(msg)
        server.quit()

        # スプレッドシートを更新
        row = urls.index(url) + 1  # インデックスから行番号に変換
        sheet.update_cell(row, 2, '在庫あり')  # B列
        sheet.update_cell(row, 3, time.strftime('%H:%M:%S'))  # C列

driver.quit()
