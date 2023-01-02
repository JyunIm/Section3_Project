### ML 모델 ###
# 라이브러리 불러오기
import pandas as pd
import numpy as np
import re
import os
import io
import psycopg2
import pickle
from dotenv import load_dotenv
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split, cross_val_predict, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from xgboost import XGBClassifier

# 환경변수 가져오기
load_dotenv()
psycopg_host = os.getenv('ELEPHANTSQL_HOST')
psycopg_db = os.getenv('ELEPHANTSQL_DB')
psycopg_user = os.getenv('ELEPHANTSQL_USER')
psycopg_password = os.getenv('ELEPHANTSQL_PASSWORD')

# DB에서 데이터 불러오기
conn = psycopg2.connect(
    host = psycopg_host,
    database = psycopg_db,
    user = psycopg_user,
    password = psycopg_password
)

cur = conn.cursor()
cur.execute('SELECT * FROM public.naver;')
naver = cur.fetchall()
cur.execute('SELECT * FROM public.store;')
store = cur.fetchall()

naver = np.array(naver)
naver = pd.DataFrame(data=naver, columns = ['id','name','price','delivery_fee','category', 'etc'])
store = np.array(store)
store = pd.DataFrame(data=store, columns = ['id','name','review_star','menu','view_count','review_count','city'])

# EDA 진행
df1 = naver.copy()
df1['review'] = None
df1['sales'] = None
df1['price'] = df1['price'].str.replace(',','').str.extract(r'(\d+)')
df1['delivery_fee'] = df1['delivery_fee'].str.replace(',','').str.extract(r'(\d+)')
for i in range(len(df1)):
  df1['category'][i] = df1['category'][i].replace('식품밀키트','')
  df1['review'][i] = df1['etc'][i].split(' ')[0]
  df1['sales'][i] = df1['etc'][i].split(' ')[-1]
  if df1['sales'][i].find('구매건수'):
    df1['sales'][i] = 0
  else:
    pass
df1['review'] = df1['review'].str.replace(',','').str.extract(r'(\d+)')
df1['sales'] = df1['sales'].str.replace(',','').str.extract(r'(\d+)')
df1.drop(columns='etc', inplace=True)
df1[['price','delivery_fee','review','sales']] = df1[['price','delivery_fee','review','sales']].astype(float)
df1[['delivery_fee','review','sales']] = df1[['delivery_fee','review','sales']].fillna(0)
df1['target'] = None
for i in range(len(df1)):
  if df1['sales'][i] >= df1['sales'].quantile(0.95):
    df1['target'][i] = 1
  else :
    df1['target'][i] = 0
df1.category = df1.category.map({'찌개/국':1, '간식/디저트':2, '볶음/튀김':3,'구이':4,'면/파스타':5})
df1[['category','target']] = df1[['category','target']].astype(int)

# 모델학습 
feature = ['price','delivery_fee','category','review']
train, test = train_test_split(df1, test_size=0.2, random_state=42)
train, val = train_test_split(train, test_size=0.2, random_state=42)
X_train = train[feature]
y_train = train['target']
X_val = val[feature]
y_val = val['target']
X_test = test[feature]
y_test = test['target']

def model_train(X_train, y_train, X_val, y_val, model):
  X_train_ = X_train.copy()
  y_train_ = y_train.copy()
  X_val_ = X_val.copy()
  y_val_ = y_val.copy()
  model.fit(X_train_, y_train_)
  y_pred = model.predict(X_val_)
  print('F1 Score : ', f1_score(y_val_, y_pred).round(2))
  print('Accuracy : ', accuracy_score(y_val_, y_pred).round(2))
  print('AUC Score : ', roc_auc_score(y_val_, y_pred).round(2))

rf_model = RandomForestClassifier(class_weight='balanced',random_state=42)
dt_model = DecisionTreeClassifier(class_weight='balanced',random_state=42)
lo_model = LogisticRegression(class_weight='balanced',random_state=42)
locv_model = LogisticRegressionCV(class_weight='balanced',random_state=42)
boo_model = XGBClassifier(eval_metric = 'auc',scale_pos_weight=(y_val == 0).sum()/(y_val==1).sum(), random_state=42)

# print('RandomForest')
# model_train(X_train, y_train, X_val, y_val, rf_model)
# print('\nDecisionTree')
# model_train(X_train, y_train, X_val, y_val, dt_model)
# print('\nLogisticRegression')
# model_train(X_train ,y_train, X_val, y_val, lo_model)
# print('\nLogisticRegressionCV')
# model_train(X_train, y_train, X_val, y_val, locv_model)
# print('\nXGBClassifier')
# model_train(X_train, y_train, X_val, y_val, boo_model)

# 모델 선택 및 최종 결과 확인
model = lo_model
model.fit(X_train, y_train)
y_pred = model.predict(X_val)
print("검증 데이터 성능 확인")
print('F1 Score : ', f1_score(y_val, y_pred).round(2))
print('Accuracy : ', accuracy_score(y_val, y_pred).round(2))
print('AUC Score : ', roc_auc_score(y_val, y_pred).round(2))
y_pred = model.predict(X_test)
print('\n테스트 데이터 성능 확인')
print('F1 Score : ', f1_score(y_test, y_pred).round(2))
print('Accuracy : ', accuracy_score(y_test, y_pred).round(2))
print('AUC Score : ', roc_auc_score(y_test, y_pred).round(2))

# 모델 부호화
with open('model.pkl', 'wb') as pickle_file:
    pickle.dump(model, pickle_file)


## 데이터 분석
df2 = store.copy()
for i in range(len(df2.review_star)):
  if df2.review_star[i] == '':
    df2.review_star[i] = 0
  else :
    pass
df2.review_star = df2.review_star.astype(float)
for i in range(len(df2.review_count)):
  if df2.review_count[i] == '':
    df2.review_count[i] = 0
  else :
    pass
for i in range(len(df2.view_count)):
  if df2.view_count[i] == '':
    df2.view_count[i] = 0
  else :
    pass
df2[['view_count','review_count']] = df2[['view_count','review_count']].astype(int)
df2.drop(columns='id', inplace=True)
df2 = df2.drop_duplicates()
df2_ = df2.query('review_star >= 4.6 and view_count >= 197695 and review_count >= 162')
df2_ = df2_.sort_values(by = 'view_count',ascending=False)
df2_.reset_index(drop=True, inplace=True)
df2_['naver_review_count'] = None
df2_['average_price_of_menu'] = None
df2_['naver_review_count'][0] = 1934
df2_['average_price_of_menu'][0] = 17000

df2_['naver_review_count'][1] = 1534
df2_['average_price_of_menu'][1] = 39000

df2_['naver_review_count'][2] = 466
df2_['average_price_of_menu'][2] = 25000

df2_['naver_review_count'][3] = 2293
df2_['average_price_of_menu'][3] = 27500

df2_['naver_review_count'][4] = 916
df2_['average_price_of_menu'][4] = 3300

df2_['naver_review_count'][5] = 1051
df2_['average_price_of_menu'][5] = 26500

df2_['naver_review_count'][6] = 3822
df2_['average_price_of_menu'][6] = 22900

df2_['naver_review_count'][7] = 3522
df2_['average_price_of_menu'][7] = 17000

df2_['naver_review_count'][8] = 2183
df2_['average_price_of_menu'][8] = 41000

df2_['naver_review_count'][9] = 2609
df2_['average_price_of_menu'][9] = 24000

df2_['naver_review_count'][10] = 619
df2_['average_price_of_menu'][10] = 16000

df2_['naver_review_count'][11] = 2429
df2_['average_price_of_menu'][11] = 14000

cur.execute('DROP TABLE IF EXISTS top12_store')
cur.execute('''CREATE TABLE top12_store (
  name VARCHAR(255),
  review_star FLOAT,
  menu VARCHAR(255),
  view_count INTEGER,
  review_count INTEGER,
  city VARCHAR(255),
  naver_review_count INTEGER,
  average_price_of_menu INTEGER);''')

for i in range(len(df2_)):
  cur.execute(f"""INSERT INTO top12_store VALUES (
    '{df2_['name'][i]}','{df2_['review_star'][i]}','{df2_['menu'][i]}',
    '{df2_['view_count'][i]}','{df2_['review_count'][i]}','{df2_['city'][i]}',
    '{df2_['naver_review_count'][i]}','{df2_['average_price_of_menu'][i]}'
    );""")

conn.commit()
conn.close()