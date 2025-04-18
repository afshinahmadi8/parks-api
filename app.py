from flask import Flask, request, jsonify
import psycopg2
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD")
)
cursor = conn.cursor()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    lat, lng = map(float, data['coordinates'].split(','))
    cursor.execute("""
        INSERT INTO citizen_reports (park_name, issue_type, description, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
    """, (data['parkName'], data['issueType'], data['description'], lng, lat))
    conn.commit()

    # اجرای تابع اعتبارسنجی مکانی
    cursor.execute("SELECT validate_reports();")
    conn.commit()

    return jsonify({'message': 'گزارش با موفقیت ثبت شد'})

if __name__ == '__main__':
    app.run()
