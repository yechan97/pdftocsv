from flask import Flask, render_template, request, send_file, jsonify
import pdfplumber
import re
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    file = request.files['pdf']
    if file:
        with pdfplumber.open(file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()

        pattern = re.compile(r"(\S+)\s(\d+):(\d+)\s(.+?)(?=\S+\s\d+:\d+|\Z)", re.DOTALL)
        matches = pattern.findall(text)

        data = []
        for match in matches:
            book, chapter, verse, content = match
            data.append({"책": book, "장": chapter, "절": verse, "내용": content.strip()})

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
    return jsonify({"error": "파일을 업로드 해주세요."}), 400

if __name__ == '__main__':
    app.run(debug=True)

