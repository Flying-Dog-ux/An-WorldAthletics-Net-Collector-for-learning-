from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from cleaned import clean
from tqdm import tqdm
import pandas as pd
import random
import time
import json


def set_web():
    # 创建一个浏览器实例
    Op = Options()
    # 呜呜呜——无头模式启动！
    Op.add_argument("-headless") 
    
    # 提示：有时无头模式会被网站检测，建议加个大一点的窗口分辨率
    Op.add_argument("--width=1920")
    Op.add_argument("--height=1080")
    web = webdriver.Firefox(service=Service('.\\geckodriver.exe'),options= Op)

    wait = WebDriverWait(web, 15)

    return wait, web

def search_text():
    wait, web = set_web()
    web.get("https://worldathletics.org/world-rankings/marathon/men")
    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table-row--hover')))
    
    
    rows = web.find_elements(By.CSS_SELECTOR, "tr[class*='table-row']")
        
    print(f"找到 {len(rows)} 条排名数据：")
    for row in tqdm(rows, desc="马拉松选手数据抓取中", unit="人"):
        try:
            # 1. 找到这一行里可以点击的那个元素（比如运动员名字或得分）
            # 假设点击整行就能弹出窗口
            web.execute_script("arguments[0].click();", row)
            
            # 2. 等待弹窗加载
            time.sleep(2) 
            
            # 3. 抓取数据
            result_data = get_modal_data(web)
            with open('athletes_data.json', 'a', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False)
                f.write('\n')
                f.close()
            
            # 4. 关键：抓完要关闭弹窗！否则点不了下一行
            # 找到弹窗的关闭按钮 (通常是 class 包含 close 的按钮)
            # close_btn = web.find_element(By.CSS_SELECTOR, ".close") 
            # close_btn.click()
            # 为防止让您看到报错而产生精神障碍（bushi），我贴心地使用了Esc键
            ActionChains(web).send_keys(Keys.ESCAPE).perform()
            time.sleep(random.uniform(0.5,1))
            
        except Exception as e:
            print(f"处理行时出错: {e}")
            continue
    web.quit()

def get_modal_data(web):
    # 等待弹窗中的表格出现
    try:
        table = WebDriverWait(web, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.records-table.dark"))
        )
        
        # 获取表头
        headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
        
        # 获取所有行数据
        results = []
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

        print(f" 开始抓取，共计 {len(rows)} 名运动员...")
        
        try:
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    # 将表头和单元格内容对应起来，做成字典
                    row_dict = {headers[i]: cells[i].text for i in range(len(cells))}
                    results.append(row_dict)
        except Exception as e:
            # 进度条运行中如果打印报错，tqdm.write 可以防止进度条被打乱
            tqdm.write(f"⚠️ 处理某行时跳过: {e}")
            

        return {"headings": headers, "results": results}
    except Exception as e:
        print(f"提取弹窗数据失败: {e}")
        return {"headings": [], "results": []}

# def box_click(wait, web, selector):
    
#     aim = web.find_element(By.CSS_SELECTOR, selector)
#     web.execute_script("arguments[0].click();", aim)

def main():
    search_text()
    
    
    
if __name__ == "__main__":
    main()
    
    print("成功！正在加载数据：")

    df = pd.read_json("athletes_data.json", lines=True)
    df.to_excel("athletes_data.xlsx", index=False)

    clean()