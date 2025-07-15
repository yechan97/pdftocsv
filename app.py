from flask import Flask, render_template, request, send_file
import pdfplumber
import pandas as pd
import io
import os
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if uploaded_file is None or uploaded_file.filename == '':
        return '파일을 선택해주세요.', 400

    with pdfplumber.open(uploaded_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # 간단한 예제 기준 regex
    pattern = re.compile(r"(\S+)\s(\d+):(\d+)\s(.+?)(?=\S+\s\d+:\d+|\Z)", re.DOTALL)
    matches = pattern.findall(text)

    rows = []
    for match in matches:
        rows.append({
            '책': match[0],
            '장': match[1],
            '절': match[2],
            '내용': match[3].strip()
        })

    df = pd.DataFrame(rows)

    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False, encoding='utf-8-sig')
    csv_io.seek(0)

    return send_file(
        io.BytesIO(csv_io.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='성경DB.csv'
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
