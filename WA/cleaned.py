import pandas as pd
import ast

def clean():
    # 1. 加载你那“有形的一坨”
    df_messy = pd.read_excel("athletes_data.xlsx")

    # 2. 预处理：去掉空的行
    df_messy = df_messy[df_messy['results'] != '[]'].copy()

    # 3. 核心清洗逻辑：将字符串转回列表并展开
    all_records = []

    for index, row in df_messy.iterrows():
        # 因为 CSV 会把列表存成字符串，我们用 ast.literal_eval 把它还原成真正的 Python 列表
        try:
            results_list = ast.literal_eval(row['results'])
            for race in results_list:
                all_records.append(race)
        except:
            continue

    # 4. 生成真正清爽的表格
    df_clean = pd.DataFrame(all_records)

    # 5. 细节美化：转换日期格式，让它能被 Excel 识别为日期
    df_clean['Date'] = pd.to_datetime(df_clean['Date'], format='%d %b %Y' ,errors='coerce')

    # 6. 排序：按分数或日期排序
    df_clean = df_clean.sort_values(by='Pf.Sc', ascending=False)

    # 7. 导出
    df_clean.to_excel("marathon_clean_data.xlsx", index=False)
    print("清洗完成！你的数据现在‘眉清目秀’了。")