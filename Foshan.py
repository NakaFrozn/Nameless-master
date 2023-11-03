import pandas as pd
from ltp import LTP
import re

ltp = LTP()

src_name = 'xiamen.xlsx'  # 原始文件
tar_name = 'xm_clean.xlsx' # 中间生成文件
res_name = 'xm_res.xlsx' # 最终生成文件

def get_time_content(src_name, tar_name):
    df = pd.read_excel(src_name, engine='openpyxl', header=0)

    cleaned_data = {'time':df['时间'], 'content':df['正文']}
    cleaned_data_df = pd.DataFrame(cleaned_data)
    cleaned_data_df = cleaned_data_df.groupby(by='time').sum()
    cleaned_data_df.to_excel(tar_name)

def process(text):
    with open('professions.txt', 'r', encoding='utf-8') as f:
        profession = f.read().split('\n')

    seg, hidden = ltp.seg([text])
    ner = ltp.ner(hidden) # 命名实体识别，nh姓名，ni机构，ns地点

    name = []
    place = []
    action = []
    work = []

    p1 = r'男|女'
    p2 = r'岁'
    age = re.findall(p2, text) # 年龄
    gender = re.findall(p1, text) # 性别
    for i in profession:
        if i in text and i != '员':
            work.append(i) # 职业
    
    for i in range(len(ner[0])): # 遍历识别出的所有实体
        tag, start, end = ner[0][i]
        if tag == 'Nh':
            name.append(''.join(seg[0][start: end+1])) # 姓名
        elif tag == 'Ns' or tag == 'Ni':
            place.append(''.join(seg[0][start: end+1])) # 地点
    
    pos = ltp.pos(hidden) # 词性标注，提取出动词
    for i in range(len(seg[0])):
        if pos[0][i] == 'v':
            action.append(seg[0][i]) # 动作

    if len(name) == 0:
        name_label = 0
    elif '某' in name:
        name_label = 0.5
    else:
        name_label = 1

    age_label = 1 if len(age) != 0 else 0
    gender_label = 1 if len(gender) != 0 else 0
    work_label = 1 if len(work) != 0 else 0

    return (name, name_label, age, age_label, gender, gender_label, work, work_label, place, action)

if __name__ == '__main__':
    get_time_content(src_name, tar_name)

    clean_data_df = pd.read_excel(tar_name, engine='openpyxl', header=0)

    name_col = []
    name_label_col = []
    age_col = []
    age_label_col = []
    gender_col = []
    gender_label_col = []
    work_col = []
    work_label_col = []
    place_col = []
    action_col = []

    for i in clean_data_df['content']:
        if i != 0:
            name, name_label, age, age_label, gender, gender_label, work, work_label, place, action = process(i)
            name_col.append(name)
            name_label_col.append(name_label)
            age_col.append(age)
            age_label_col.append(age_label)
            gender_col.append(gender)
            gender_label_col.append(gender_label)
            work_col.append(work)
            work_label_col.append(work_label)
            place_col.append(list(set(place)))
            action_col.append(list(set(action)))
        else:
            name_col.append([])
            name_label_col.append(0)
            age_col.append([])
            age_label_col.append(0)
            gender_col.append([])
            gender_label_col.append(0)
            work_col.append([])
            work_label_col.append(0)
            place_col.append([])
            action_col.append([])

    result_data = {'time' :        clean_data_df['time'], 
                   'content':      clean_data_df['content'], 
                   'name':         name_col,  
                   'name_label':   name_label_col,
                   'age':          age_col,
                   'age_label':    age_label_col,
                   'gender':       gender_col,
                   'gender_label': gender_label_col,
                   'work':         work_col,
                   'work_label':   work_label_col,
                   'place':        place_col,
                   'action':       action_col}
    result = pd.DataFrame(result_data)
    print(result)
    result.to_excel(res_name)