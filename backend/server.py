from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import os
import base64
from datetime import datetime, timedelta
import logging
from statistics import mean

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24) #セッション用の秘密鍵

# SQLiteデータベースの作成
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS measurements
             (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, weight REAL, sleep_hours REAL)''')
conn.commit()

# SQLiteデータベースの作成
conn = sqlite3.connect('user.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
conn.commit()


#ユーザー登録
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        #パスワードをハッシュ化
        hashe_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashe_password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 200

# ログイン
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        
        # パスワードをハッシュ化
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        #ユーザー名とパスワードをデータベースから検索
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = c.fetchone()

        if user:
            #ログイン成功時の処理
            session['logged_in'] = True
            session['user_id'] = user[0] #ユーザーIDをセッションに保存
            return jsonify({'message': 'Login successful', 'user_id': user[0]}), 200
        else:
            #ログイン失敗時の処理    
            return jsonify({'message': 'Invalid credentials'}), 401
        

# ログアウト
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# データの保存
@app.route('/save_data', methods=['POST'])
def save_data():
 
    data = request.json
    weight = data['weight']
    sleep_hours = data['sleep_hours']
    date = datetime.now().strftime("%Y-%m-%d")

    #ログインしているユーザーのIDを取得
    user_id = data['user_id']

    conn = sqlite3.connect('data.db') 
    c = conn.cursor()

    #今日の日付で保存されたデータがあるかどうかを確認
    c.execute("SELECT * FROM measurements WHERE user_id = ? AND date = ?", (user_id, date))
    existing_data = c.fetchone()

    if existing_data:
        conn.close()
        return jsonify({'message': '＊今日のデータは既に保存されています。'}), 400

    #今日のデータがない場合、新しいデータを挿入 
    c.execute("INSERT INTO measurements (user_id, date, weight, sleep_hours) VALUES (?,?, ?, ?)", (user_id, date, weight, sleep_hours))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Data saved successfully'}), 200

# データの取得と可視化
@app.route('/visualize', methods=['GET'])
def visualize():
    #パラメーターからユーザーIDを取得
    user_id = request.args.get('user_id')

    #データベースからデータを取得
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM measurements WHERE user_id = ?", (user_id,))
    data = c.fetchall()
    conn.close()

    # データを日付でソートする
    data = sorted(data, key=lambda x: datetime.strptime(x[2], "%Y-%m-%d"))

    #日付の範囲を取得
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    #日付の範囲内の毎日の日付を生成
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    weights = []
    sleep_hours = []
    for date in dates:
        # 日付がデータベースの中に存在するかどうかをチェック
        date_str = date.strftime("%Y-%m-%d")
        for row in data:
            if row[2] == date_str:
                weights.append(row[3])
                sleep_hours.append(row[4])
                break
        else:
            # 日付に対応するデータが存在しない場合は、Noneを追加
            weights.append(None)
            sleep_hours.append(None)

    # グラフの作成
    plt.close('all')  # 前のプロットをすべて閉じる
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # 日付のメモリを設定
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # 左側のy軸で体重をプロット
    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Weight', color=color)
    ax1.plot(dates, weights, marker='o', color=color, label='Weight')  # 体重をプロット
    ax1.tick_params(axis='y', labelcolor=color)

    # 右側の y 軸を追加して睡眠時間をプロット
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Sleep Hours', color=color)
    ax2.plot(dates, sleep_hours, marker='o', color=color, label='Sleep Hours')  # 睡眠時間をプロット
    ax2.tick_params(axis='y', labelcolor=color)

    # 体重の y 軸の範囲を設定
    ax1.set_ylim(0, 100)
    # 睡眠時間の y 軸の範囲を設定
    ax2.set_ylim(0, 12)

    plt.xlim(dates[0], dates[-1])

    plt.title('Weight and Sleep Hours Over Time')
    fig.tight_layout()
    
    # グラフをバイナリデータに変換
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Base64エンコード
    image_base64 = base64.b64encode(image_png).decode()

    return jsonify({'image': image_base64}), 200

#過去一か月間の平均体重と平均睡眠時間を計算する
@app.route('/average_data', methods=['GET'])
def average_data():
    #パラメータからユーザーIDを取得
    user_id = request.args.get('user_id')

    #データベースからデータを取得
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM measurements WHERE user_id = ?", (user_id,))
    data = c.fetchall()
    conn.close()

    # データを日付でソートする
    data = sorted(data, key=lambda x: datetime.strptime(x[2], "%Y-%m-%d"))

    #過去一か月間のデータを抽出
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    data_within_month = [row for row in data if start_date <= datetime.strptime(row[2], "%Y-%m-%d") <= end_date]

    #体重と睡眠時間のリストを作成
    weights = [row[3] for row in data_within_month if row[3] is not None]
    sleep_hours = [row[4] for row in data_within_month if row[4] is not None]

    # 平均体重と平均睡眠時間を計算
    average_weight = mean(weights)
    average_sleep_hours = mean(sleep_hours)

    # フロントエンドに平均値を返す
    return jsonify({'average_weight': average_weight, 'average_sleep_hours': average_sleep_hours}), 200


if __name__ == '__main__':
    app.run(debug=True)