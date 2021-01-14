import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta

# 타겟 URL을 읽어서 HTML를 받아오고,
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data1 = requests.get('https://finance.naver.com/sise/sise_rise.nhn', headers=headers)
data2 = requests.get('https://finance.naver.com/sise/sise_fall.nhn', headers=headers)

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
# soup이라는 변수에 "파싱 용이해진 html"이 담긴 상태가 됨
# 이제 코딩을 통해 필요한 부분을 추출하면 된다.
soup1 = BeautifulSoup(data1.text, 'html.parser')
soup2 = BeautifulSoup(data2.text, 'html.parser')

# soup4 = BeautifulSoup(data1.text, 'html.parser')


# contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td.no /순위
# contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td:nth-child(2) > a /주식명
# contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td:nth-child(3) /현재가
# contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td:nth-child(4) > span
# contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td:nth-child(5) > span
# contentarea > div.box_type_l > table > tbody > tr:nth-child(3) > td:nth-child(6)
# content > div.section.trade_compare > h4 > em > a

import datetime

dateindicator = datetime.datetime.today().strftime('%y-%m-%d')


@app.route('/today', methods=['GET'])
def today_write():
    return jsonify({'result': 'success', 'today': dateindicator})


# select를 이용해서, tr들을 불러오기
stocks1 = soup1.select('#contentarea > div.box_type_l > table > tr')
stocks2 = soup2.select('#contentarea > div.box_type_l > table > tr')

cnt1 = 0
cnt2 = 0
# print("\n오늘의 상승주 TOP10\n")

db.stocks1.delete_many({})
for stock1 in stocks1:

    rank1 = stock1.select_one('td.no')
    name1 = stock1.select_one('td:nth-child(2) > a')
    price1 = stock1.select_one('td:nth-child(3)')
    ratio1 = stock1.select_one('td:nth-child(4) > span')
    percent1 = stock1.select_one('td:nth-child(5) > span')
    amount1 = stock1.select_one('td:nth-child(6)')
    link1 = stock1.select_one('td:nth-child(2) > a')

    if rank1 != None and name1 != None and price1 != None and link1 != None:

        url1 = 'https://finance.naver.com' + link1['href']
        data3 = requests.get('https://finance.naver.com' + link1['href'], headers=headers)
        soup3 = BeautifulSoup(data3.text, 'html.parser')
        type1 = soup3.select_one(' #content > div.section.trade_compare > h4 > em > a')

        if type1 == None:
            type1_text = 'ETF'
        else:
            type1_text = type1.text

        # if type1 != None:
        # print(type1.text)

        # print(dateindicator, rank1.text, type1_text, name1.text, price1.text.strip(), ratio1.text.strip(), percent1.text.strip(), amount1.text)
        review1 = {
            'date': dateindicator,
            'rank': rank1.text,
            'type': type1_text,
            'name': name1.text,
            'price': price1.text.strip(),
            'ratio': ratio1.text.strip(),
            'percent': percent1.text.strip(),
            'amount': amount1.text,
            'url': url1
        }
        db.stocks1.insert_one(review1)
        db.stocks3.insert_one(review1)

        cnt1 = cnt1 + 1
        if cnt1 == 20:
            break

# print(ratio1.text)
# print("\n오늘의 하락주 TOP10\n")
db.stocks2.delete_many({})
for stock2 in stocks2:
    rank2 = stock2.select_one('td.no')
    name2 = stock2.select_one('td:nth-child(2) > a')
    price2 = stock2.select_one('td:nth-child(3)')
    ratio2 = stock2.select_one('td:nth-child(4) > span')
    percent2 = stock2.select_one('td:nth-child(5) > span')
    amount2 = stock2.select_one('td:nth-child(6)')
    link2 = stock2.select_one('td:nth-child(2) > a')

    if rank2 != None and name2 != None and price2 != None and link2 != None:

        url2 = 'https://finance.naver.com' + link2['href']
        data4 = requests.get('https://finance.naver.com' + link2['href'], headers=headers)
        soup4 = BeautifulSoup(data4.text, 'html.parser')
        type2 = soup4.select_one(' #content > div.section.trade_compare > h4 > em > a')
        if type2 == None:
            type2_text = 'ETF'
        else:
            type2_text = type2.text

        # print(rank2.text, type2_text, name2.text, price2.text.strip(), ratio2.text.strip(), percent2.text.strip(), amount2.text)
        # print(url2)
        review2 = {
            'date': dateindicator,
            'rank': rank2.text,
            'type': type2_text,
            'name': name2.text,
            'price': price2.text.strip(),
            'ratio': ratio2.text.strip(),
            'percent': percent2.text.strip(),
            'amount': amount2.text,
            'url': url2
        }
        db.stocks2.insert_one(review2)
        db.stocks4.insert_one(review2)

        cnt2 = cnt2 + 1
        if cnt2 == 20:
            break


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')


# ## API 역할을 하는 부분
# @app.route('/review', methods=['POST'])
# def read_today():
#     # review_receive로 클라이언트가 준 review 가져오기
#     review_receive = request.form['review_write']
#
#     # # DB에 삽입할 정보 만들기
#     # review1 = {
#     #     'rank': rank1.text,
#     #     'type': type1_text,
#     #     'name': name1.text,
#     #     'price': price1.text.strip(),
#     #     'ratio': ratio1.text.strip(),
#     #     'percent': percent1.text.strip(),
#     #     'amount': amount1.text
#     # }
#     # # reviews에 review 저장하기
#     # db.stocks.insert_one(review1)
#     # 성공 여부 & 성공 메시지 반환
#     return jsonify({'result': 'success', 'msg': '리뷰가 성공적으로 작성되었습니다.'})

@app.route('/rank1', methods=['GET'])
def today_rank1():
    # 1. DB에서 리뷰 정보 모두 가져오기
    rank1 = list(db.stocks1.find({}, {'_id': 0}))
    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'reviews': rank1})


@app.route('/rank2', methods=['GET'])
def today_rank2():
    # 1. DB에서 리뷰 정보 모두 가져오기
    rank2 = list(db.stocks2.find({}, {'_id': 0}))
    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'reviews': rank2})

@app.route('/bookMark', methods=['GET'])
def book_mark():
    # 1. DB에서 리뷰 정보 모두 가져오기
    bookmark1 = list(db.stocks3.find({}, {'_id': 0}))
    bookmark2 = list(db.stocks4.find({}, {'_id': 0}))
    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'review1': bookmark1, 'review2': bookmark2})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
