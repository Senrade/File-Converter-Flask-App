import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pandas as pd
from pdf2image import convert_from_path
import pdfplumber
from docx import Document
from docx2pdf import convert as docx_to_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

# Allowed input formats
ALLOWED_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'txt', 'png', 'jpg', 'jpeg', 'docx'}

# Logic conversions
VALID_CONVERSIONS = {
    'pdf':   ['txt', 'png', 'jpg', 'docx'],
    'csv':   ['pdf', 'xlsx', 'txt'],
    'xlsx':  ['pdf', 'csv', 'txt'],
    'txt':   ['pdf', 'csv', 'xlsx', 'docx'],
    'png':   ['jpg'],
    'jpg':   ['png'],
    'jpeg':  ['png'],
    'docx':  ['pdf', 'txt']
}

# --- Utility functions ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_txt(input_path, output_path):
    """Extract text from PDF into a TXT file."""
    text = ""
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def txt_to_docx(input_path, output_path):
    """Convert plain text file to a Word document."""
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(output_path)

def docx_to_txt(input_path, output_path):
    """Extract text from a Word document into TXT."""
    doc = Document(input_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

def pdf_to_docx(input_path, output_path):
    """Convert PDF text to Word document (layout not preserved)."""
    doc = Document()
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                doc.add_paragraph(extracted)
    doc.save(output_path)

def convert_file(input_path, output_path, input_ext, output_ext):
    """
    Handle file conversion by type pairing.
    Each branch uses the right library to avoid NoneType errors.
    """

    # --- PDF conversions ---
    if input_ext == 'pdf' and output_ext == 'txt':
        pdf_to_txt(input_path, output_path)

    elif input_ext == 'pdf' and output_ext in ['png', 'jpg']:
        images = convert_from_path(input_path)
        if images:
            images[0].save(output_path, output_ext.upper())

    elif input_ext == 'pdf' and output_ext == 'docx':
        pdf_to_docx(input_path, output_path)

    # --- DOCX conversions ---
    elif input_ext == 'docx' and output_ext == 'txt':
        docx_to_txt(input_path, output_path)

    elif input_ext == 'docx' and output_ext == 'pdf':
        # docx2pdf writes to same directory
        temp_dir = os.path.dirname(output_path)
        os.makedirs(temp_dir, exist_ok=True)
        docx_to_pdf(input_path, temp_dir)
        generated_pdf = os.path.join(temp_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
        os.rename(generated_pdf, output_path)

    # TXT to DOCX
    elif input_ext == 'txt' and output_ext == 'docx':
        txt_to_docx(input_path, output_path)

    # --- CSV / XLSX / TXT conversions ---
    elif input_ext in ['csv', 'xlsx', 'txt'] and output_ext in ['csv', 'xlsx', 'pdf', 'txt']:
        if input_ext == 'csv':
            df = pd.read_csv(input_path, encoding='utf-8')
        elif input_ext == 'xlsx':
            df = pd.read_excel(input_path)
        elif input_ext == 'txt' and output_ext != 'docx':  # exclude txt->docx handled earlier
            df = pd.read_csv(input_path, sep="\t", engine="python")

        if output_ext == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif output_ext == 'xlsx':
            df.to_excel(output_path, index=False)
        elif output_ext == 'pdf':
            html = df.to_html(index=False)
            with open("temp.html", "w", encoding="utf-8") as f:
                f.write(html)
            os.rename("temp.html", output_path)  # Placeholder for PDF generation
        elif output_ext == 'txt':
            df.to_csv(output_path, sep="\t", index=False, encoding='utf-8')

    # --- Image conversions ---
    elif input_ext in ['png', 'jpg', 'jpeg'] and output_ext in ['png', 'jpg']:
        img = Image.open(input_path)
        img.save(output_path)

    else:
        raise ValueError("Unsupported conversion requested.")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_formats/<ext>')
def get_formats(ext):
    ext = ext.lower()
    formats = VALID_CONVERSIONS.get(ext, [])
    return jsonify(formats)

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if not allowed_file(file.filename):
        return "Invalid file type", 400

    target_format = request.form.get('format')
    if not target_format:
        return "No target format selected", 400

    filename = secure_filename(file.filename)
    input_ext = filename.rsplit('.', 1)[1].lower()

    if target_format not in VALID_CONVERSIONS.get(input_ext, []):
        return "Invalid conversion type", 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}.{target_format}"
    output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

    try:
        convert_file(input_path, output_path, input_ext, target_format)
    except Exception as e:
        return f"Error during conversion: {e}", 500

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)