from flask import Blueprint, render_template, escape, request, Response, g, make_response
import pickle
import pandas as pd
import numpy as np

part3 = Blueprint('part3', __name__, url_prefix = '/predict')

@part3.route('/')
def get_value():
    return render_template('get_value.html')

@part3.route('/result', methods=['GET','POST'])
def result_value():
    model = None
    with open('project/model.pkl','rb') as pickle_file:
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
    return render_template('result_value.html', name = name, result = result)
