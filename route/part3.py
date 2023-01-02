from flask import Blueprint, render_template, escape, request, Response, g, make_response
import pickle
import pandas as pd
import numpy as np
import psycopg2
from dotenv import load_dotenv
import os

# 환경변수 가져오기
load_dotenv()
psycopg_host = os.getenv('ELEPHANTSQL_HOST')
psycopg_db = os.getenv('ELEPHANTSQL_DB')
psycopg_user = os.getenv('ELEPHANTSQL_USER')
psycopg_password = os.getenv('ELEPHANTSQL_PASSWORD')


part3 = Blueprint('part3', __name__, url_prefix = '/predict')

@part3.route('/')
def get_value():
    return render_template('get_value.html')

@part3.route('/result', methods=['GET','POST'])
def result_value():
    model = None
    with open('model.pkl','rb') as pickle_file:
        model = pickle.load(pickle_file)
    if request.method == 'POST':
        # 입력값 받기
        name = request.form['store_name']
        category = request.form['menu']
        price = request.form['price']
        delivery_fee = request.form['delivery_fee']
        review = request.form['review_count']
        value = [int(price), int(delivery_fee), int(category), int(review)]
        value = np.array(value)
        value = value.reshape(1,-1)
        results = model.predict(value)
        if results == 1:
            result = '출시 시, 전체 중 95%의 상품보다 잘 팔릴 것으로 예상됩니다.'
        else : 
            result = '다른 상품을 준비해주세요.'
        # 결과값 DB에 저장
        conn = psycopg2.connect(
            host = psycopg_host,
            database = psycopg_db,
            user = psycopg_user,
            password = psycopg_password
        )
        cur = conn.cursor()
        # cur.execute('''CREATE TABLE meal_kit_predict (
        #     name VARCHAR(255),
        #     menu VARCHAR(255),
        #     price INTEGER,
        #     naver_review_count INTEGER,
        #     delivery_fee INTEGER,
        #     results VARCHAR(255));''')
        cur.execute(f"""INSERT INTO meal_kit_predict VALUES (
            '{name}','{category}','{price}',
            '{review}','{delivery_fee}','{result}');""")
        conn.commit()
        conn.close()
    return render_template('result_value.html', name = name, result = result)
