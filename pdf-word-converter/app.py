from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from docx2pdf import convert as docx2pdf_convert

app = Flask(__name__)
app.secret_key = "supersecretkey"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
CONVERTED_FOLDER = os.path.join(BASE_DIR, "converted")
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        flash('Dosya bulunamadı.')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi.')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        ext = filename.rsplit('.', 1)[1].lower()
        output_filename = ""
        output_path = ""
        try:
            if ext == "pdf":
                output_filename = filename.rsplit('.', 1)[0] + ".docx"
                output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
                cv = Converter(file_path)
                cv.convert(output_path, start=0, end=None)
                cv.close()
            elif ext == "docx":
                output_filename = filename.rsplit('.', 1)[0] + ".pdf"
                output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
                docx2pdf_convert(file_path, output_path)
            else:
                flash('Desteklenmeyen dosya türü.')
                return redirect(url_for('index'))
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            flash(f'Dönüştürme sırasında hata oluştu: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Geçersiz dosya türü.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)