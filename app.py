from flask import Flask, render_template, request, send_file
import pdfplumber
import pandas as pd
import io
import os
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한 예시, 필요시 더 크게

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')

    if uploaded_file is None or uploaded_file.filename == '':
        return '파일을 선택해주세요.', 400

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # 텍스트 있는 페이지만 처리
                    text += page_text + "\n"

        if not text.strip():
            return 'PDF에서 텍스트를 추출하지 못했습니다.', 400

        # 패턴 보완: 책 이름(한글+영문), 장:절, 내용
        pattern = re.compile(r"([^\s\d]+)\s(\d+):(\d+)\s(.+?)(?=\n[^\s\d]+\s\d+:\d+|\Z)", re.DOTALL)
        matches = pattern.findall(text)

        if not matches:
            return '성경 패턴과 일치하는 내용이 없습니다.', 400

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

    except Exception as e:
        print(f"오류 발생: {e}")
        return '서버에서 파일 처리 중 오류가 발생했습니다.', 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
