# 🎬 QA Evidence Auto Watermark

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue.svg)
![Status](https://img.shields.io/badge/Status-Stable-green.svg)
![Field](https://img.shields.io/badge/Field-QA_Automation-orange.svg)

## 📖 Project Overview
This automation tool was developed to streamline visual evidence preparation for bug reports. It eliminates the manual, time-consuming task of adding metadata to screenshots and screen recordings by automatically parsing bug details from an **Excel STD (Software Testing Description)** file and embedding them directly into the media files.

Featuring a fully interactive **Desktop GUI**, the engine processes both vertical and horizontal formats seamlessly, making bug evidence presentation standardized and professional.

---

## 🛠️ Advanced Features
* **Interactive Desktop GUI:** Built with modern `CustomTkinter` for a seamless user experience.
* **Multi-Threaded Architecture:** Media rendering runs on a background thread (`threading`), keeping the UI responsive and preventing freezes.
* **Excel STD Integration:** Automatically fetches Bug Summary, Severity, Category, and Date directly from an Excel sheet based on the file name (Bug ID).
* **Severity-Based Color Coding:** Dynamically changes the watermark text color based on the bug's severity (`Show Stop`, `Critical`, `Major`, `Moderate`, `Low`).
* **Intelligent Media Overlay:** * Generates a **5-second video intro slide** containing full bug specifications.
  * Applies a smart, semi-transparent watermark template that auto-adapts to **Vertical vs. Horizontal** orientations.
* **Real-Time App Console:** Built-in log terminal inside the GUI providing instant process updates.

---

## 🚀 Technical Stack
* **Language:** Python 3.x
* **GUI Framework:** CustomTkinter
* **Media Processing:** MoviePy
* **Data Parsing:** Pandas, OpenPyXL
* **Environment:** Managed via virtual environment (`venv`)

---

## 📂 Project Structure
```text
├── process_evidence.py   # Main GUI Application & Automation Engine
├── MyProject/
│   └── STD.xlsx          # Excel sheet containing Bug descriptions
├── Evidence/
│   ├── Raw/              # Input folder for raw images/videos (e.g., NF-001.mp4)
│   └── Processed/        # Output folder for watermarked, ready-to-report media
└── .gitignore            # Git exclusion rules for media and environments
```
## ⚙️ Setup & Execution
1. Clone the Repository:
git clone [https://github.com/MeirYaakovi/QA-Evidence-Auto-Watermark.git](https://github.com/MeirYaakovi/QA-Evidence-Auto-Watermark.git)
cd QA-Evidence-Auto-Watermark
2. Environment Setup
Create and activate your virtual environment, then install the required dependencies:

Create venv:
python -m venv venv

Activate venv (Windows):
.\venv\Scripts\activate

Install requirements:
pip install -r requirements.txt

3. Run the Application:
python process_evidence.py


## 🔗 Portfolios & Links
🚀 Live QA Portfolio: [meiryaakovi.github.io/MY-QA](https://meiryaakovi.github.io/MY-QA/)

## 👨‍💻 About the Developer
Name: Meir Yaakovi

Role: QA & Automation Engineer

LinkedIn: www.linkedin.com/in/meir-yaakovi

