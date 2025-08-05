# File Converter (Flask)

A simple, browser‑based file converter built with Flask.  
Upload a file, choose an available output format, and get your converted file instantly.  
Works on desktop, tablet, and mobile.

---

## Features
- **Supported input formats:** `pdf`, `csv`, `xlsx`, `txt`, `png`, `jpg`, `docx`
- **Smart conversion rules** — only valid format pairs are allowed (e.g., PNG → TXT is blocked)
- **Drag & drop** or click to upload
- **Dynamic format selection** — output list updates based on uploaded file type
- **Responsive UI** — optimized for different screen sizes

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Senrade/File-Converter-Flask-App.git
cd File-Converter-Flask-App
```

2. Create and activate a virtual environment
```bash
    python -m venv venv
```

- Activate:
  ```bash
    #In MacOS or Linux
    source venv/bin/activate

    #In CMD
    venv\Scripts\activate.bat

    #If using Powershell, doing the same in your IDE as well
    venv\Scripts\Activate.ps1

    You should see (venv) at the start of your terminal prompt.
  ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

---

## USAGE

1. Run the application
    ```bash
    python app.py
    ```

2. Access in browser
Open either URL as needed.

    * Running on http://127.0.0.1:5000        # Localhost, accessible only from this machine
    * Running on http://<your-local-ip>:5000    # LAN IP, accessible from devices on the same network

---

## Project Structure
```
file_converter/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    └── index.html
```
---

## License
This project is licensed under the MIT License.
