import sqlite3
import csv
import io
import urllib.parse
from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normal INTEGER DEFAULT 0,
            spicy INTEGER DEFAULT 0,
            set_normal INTEGER DEFAULT 0,
            set_spicy INTEGER DEFAULT 0,
            cheese INTEGER DEFAULT 0,
            mayo INTEGER DEFAULT 0,
            meat INTEGER DEFAULT 0,
            redbull INTEGER DEFAULT 0,
            total_price INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_order', methods=['POST'])
def create_order():
    normal = int(request.form.get('normal_q', 0))
    spicy = int(request.form.get('spicy_q', 0))
    set_normal = int(request.form.get('set_normal_q', 0))
    set_spicy = int(request.form.get('set_spicy_q', 0))
    cheese = int(request.form.get('cheese_q', 0))
    mayo = int(request.form.get('mayo_q', 0))
    meat = int(request.form.get('meat_q', 0))
    redbull = int(request.form.get('redbull_q', 0))
    total_price = int(request.form.get('total_price', 0))

    if total_price <= 0:
        return jsonify({'status': 'error'}), 400

    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (normal, spicy, set_normal, set_spicy, cheese, mayo, meat, redbull, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (normal, spicy, set_normal, set_spicy, cheese, mayo, meat, redbull, total_price))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/history')
def history():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, normal, spicy, set_normal, set_spicy, cheese, mayo, meat, redbull,
               strftime("%Y/%m/%d %H:%M", created_at, "localtime"), total_price
        FROM orders ORDER BY id DESC
    ''')
    orders = cursor.fetchall()
    conn.close()
    return render_template('history.html', orders=orders)

# 追加：CSVダウンロード機能
@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, normal, spicy, set_normal, set_spicy, cheese, mayo, meat, redbull,
               total_price, strftime("%Y/%m/%d %H:%M", created_at, "localtime")
        FROM orders ORDER BY id ASC
    ''')
    rows = cursor.fetchall()
    conn.close()

    # メモリ上にCSVデータを作成
    output = io.StringIO()
    writer = csv.writer(output)

    # ヘッダー行
    writer.writerow(['ID', 'ノーマル', '旨辛', 'お授けノーマル', 'お授け旨辛', 'チーズ', 'マヨネーズ', '肉増し', 'レッドブル', '合計金額', '注文時間'])

    # データ行
    for row in rows:
        writer.writerow(row)

    # ファイル名を「油そば_注文履歴.csv」に指定（日本語ファイル名の文字化け防止エンコード処理）
    filename = "油そば_注文履歴.csv"
    encoded_filename = urllib.parse.quote(filename)

    response = make_response(output.getvalue().encode('utf-8-sig'))
    response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    
    return response

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
