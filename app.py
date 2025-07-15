from flask import Flask, render_template, request, send_file, jsonify
import pdfplumber
import re
import pandas as pd
import io

app = Flask(__name__)

# 업로드 용량 최대 50MB 설정
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일명이 없습니다."}), 400

    filename = file.filename.lower()

    try:
        if filename.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                text = ''.join(page.extract_text() for page in pdf.pages)

        elif filename.endswith('.twm'):
            text = file.read().decode('utf-8')

        else:
            return jsonify({"error": "PDF 또는 TWM 파일만 지원합니다."}), 400

        pattern = re.compile(r"(\S+)\s(\d+):(\d+)\s(.+?)(?=\S+\s\d+:\d+|\Z)", re.DOTALL)
        matches = pattern.findall(text)

        data = [{"책": book, "장": chap, "절": verse, "주석": comm.strip()} for book, chap, verse, comm in matches]

        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_buffer.seek(0)

        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='성경DB.csv'
        )

    except Exception as e:
        return jsonify({"error": f"처리 중 오류가 발생했습니다: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
