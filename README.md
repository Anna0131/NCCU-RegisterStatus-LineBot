# NCCU-CheckInStatus_WebCrawler
## Background
政大放榜後，我備取在有點抖的位置，常刷政大校網查看順位比我前面的正/備取生的報到狀況。

所以我立刻就想寫一個機器人去幫我監視校網，看有沒有其他人又想報到or放棄～ ٩(๑`^´๑)۶ 

## Introduction
讓腳本模擬瀏覽器，依序選取"碩士甄試"和"對應的系所"後，就可以找到內含所有正/備取生報到狀況的表格。
（因為下拉選單的選項是動態加載的，所以有 time.sleep 一下確保 JavaScript 執行完成並更新選項）

從校網的 HTML 來看，表格內容應該是通過 JavaScript 動態載入的，這也是為什麼 requests 和 BeautifulSoup 無法直接找到報到表格的原因。
(動態生成的內容無法在初始的 HTML 中呈現，只有等到網頁執行了 JavaScript 之後才能看到完整的表格)

因此，這種情況需要使用像 Selenium 等工具，模擬瀏覽器加載網頁並執行 JavaScript，然後抓取生成的表格內容。

啊我瀏覽器選擇用 FireFox 和 GeckoDriver，因為他們的兼容性更好，更新問題較少，不然我搞 ChromeDriven 快瘋掉 = =

##  LINE Notify 
最有趣的部分就是這裡了！

我串了 LINE Notify，讓 LINE Bot 可以在有新的學生想報到時即時通知我。 _(每增加一個人要報到就很心痛..._

LINE Bot 功能包含：
1.	自動篩選「已報到」的學生，再把該學生的名字和正備取順位一併整合成一條訊息發送至 LINE。
2.	在對話框輸入 “N” 時，將已完成報到的所有人員列表傳送到 LINE。
3.	持續監控報到狀況並每 10 分鐘檢查一次。 （如果報到人數不變，就不會通知）

## Test
### Problem
因為政大校網每天凌晨會進行備份，就沒辦法爬取。

1.	手動模擬錯誤：
- 在無法訪問目標網頁，或目標元素不存在的情況下執行程式。
- 確認 error 只會簡單 print 一次，且不會中斷程式執行。
2.	正常執行：
- 確保在目標網頁結構正常時，程式能成功抓取表格內容。


## 系統畫面
<img width="286" alt="image" src="https://github.com/user-attachments/assets/9809febc-7e4d-4f90-8046-b089af7c3fde">

![image](https://github.com/user-attachments/assets/d2e3548b-d0ea-4388-97f3-335987adfc72)

![image](https://github.com/user-attachments/assets/13b5a67f-828f-4f44-a5bd-00d26e6573ef)

