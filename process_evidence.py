import os
import pandas as pd
import textwrap
import customtkinter as ctk
import threading  # הוסף כדי למנוע את קפיאת הממשק בזמן הרינדור
from tkinter import filedialog, messagebox
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip, ImageClip

# הגדרת עיצוב כללי לממשק
ctk.set_appearance_mode("System")  # מסתנכרן עם ה-Dark/Light mode של הווינדוס
ctk.set_default_color_theme("blue")


DEFAULT_LINKEDIN = "www.linkedin.com/in/Your-Name"
DEFAULT_RAW_FOLDER = "Evidence/Raw"
DEFAULT_PROCESSED_FOLDER = "Evidence/Processed"
DEFAULT_EXCEL_FILE = "MyProject/STD.xlsx"

# צבעים מותאמים אישית לפי דרגת החומרה שהגדרת
SEVERITY_COLORS = {
    "Show Stop": "red",
    "Critical": "darkred",
    "Major": "orange",
    "Moderate": "yellow",
    "Low": "green"
}


# ==========================================
# לוגיקת האוטומציה (הקוד המקורי והחכם שלך)
# ==========================================

def wrap_text(text, width):
    if not text or text == "N/A":
        return text
    wrapper = textwrap.TextWrapper(width=width, break_long_words=False, replace_whitespace=False)
    return "\n".join(wrapper.wrap(text))


def get_bug_details(bug_id, excel_file_path):
    try:
        excel_obj = pd.ExcelFile(excel_file_path, engine='openpyxl')
        first_sheet = excel_obj.sheet_names[0]
        df = pd.read_excel(excel_file_path, sheet_name=first_sheet, engine='openpyxl')
        row = df[df.iloc[:, 0].astype(str) == str(bug_id)]

        if not row.empty:
            clean = lambda val: str(val) if pd.notna(val) else "N/A"
            raw_date = row.get("Date", row.iloc[:, 3]).values[0]
            clean_date = pd.to_datetime(raw_date).date().strftime('%Y-%m-%d') if pd.notna(raw_date) else "N/A"
            category = clean(row.get("Category", row.iloc[:, 4]).values[0])
            return {
                "summary": clean(row.get("Summary", row.iloc[:, 1]).values[0]),
                "severity": clean(row.get("Severity", row.iloc[:, 2]).values[0]),
                "date": clean_date,
                "category": category
            }
    except:
        return None


def process_file(file_path, bug_id, details, processed_folder, linkedin_url, is_image=False):
    try:
        if is_image:
            source = ImageClip(file_path)
        else:
            source = VideoFileClip(file_path)

        w, h = source.size
        severity = details['severity'] if details else "N/A"
        summary = details['summary'] if details else "N/A"
        category = details['category'] if details else "N/A"
        sev_color = SEVERITY_COLORS.get(severity, "white")

        if w < h:
            wrap_width, wm_fs = 28, h // 52
            pos_x = int(w * 0.05)
            margin_y = int(h * 0.08)
        else:
            wrap_width, wm_fs = 65, h // 42
            pos_x = 'center'
            margin_y = int(h * 0.10)

        wrapped_summary = wrap_text(summary, wrap_width)
        wrapped_category = wrap_text(category, wrap_width)

        wm_content = (f"{bug_id} | {severity} | {category}\n"
                      f"{wrapped_summary}\n"
                      f"{linkedin_url}\n\n.")

        watermark = TextClip(text=wm_content, font_size=wm_fs, color=sev_color,
                             method='label', interline=5).with_opacity(0.8)

        watermark = watermark.with_duration(source.duration if not is_image else 1)
        dynamic_y = h - watermark.h - margin_y
        final_wm = watermark.with_position((pos_x, dynamic_y))

        combined = CompositeVideoClip([source, final_wm])

        if is_image:
            output_path = os.path.join(processed_folder, f"{bug_id}.png")
            combined.save_frame(output_path)
        else:
            intro_fs = h // 35 if w < h else h // 25
            intro_content = (f"ID: {bug_id}\n\nCategory:\n{wrapped_category}\n\n"
                             f"Summary:\n{wrapped_summary}\n\nSeverity: {severity}\n\n"
                             f"Date: {details['date'] if details else 'N/A'}\n\n{linkedin_url}\n\n.")

            bg_intro = ColorClip(size=(w, h), color=(0, 0, 0)).with_duration(5)
            txt_intro = TextClip(text=intro_content, font_size=intro_fs, color=sev_color,
                                 method='label', interline=10).with_duration(5)

            intro = CompositeVideoClip([bg_intro, txt_intro.with_position('center')])
            final = concatenate_videoclips([intro, combined])

            output_path = os.path.join(processed_folder, f"{bug_id}.mp4")
            final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        source.close()
    except Exception as e:
        print(f"❌ שגיאה ב-{bug_id}: {e}")


def run_automation_engine(excel, raw, processed, linkedin, log_callback, on_complete_callback):
    """פונקציית תיווך שמריצה את המנוע ומעדכנת את חלון הממשק"""
    os.makedirs(processed, exist_ok=True)

    if not os.path.exists(raw):
        log_callback(f"❌ Error: Raw folder does not exist: {raw}\n")
        on_complete_callback()
        return

    log_callback("🚀 Starting Evidence Processing Engine...\n")

    files = [f for f in os.listdir(raw) if not f.startswith('.')]
    processed_count = 0

    for filename in files:
        ext = os.path.splitext(filename)[1].lower()
        bug_id = os.path.splitext(filename)[0]
        is_video = ext in ('.mp4', '.mov')
        is_image = ext in ('.png', '.jpg', '.jpeg')

        if not (is_video or is_image): continue

        output_ext = ".mp4" if is_video else ".png"
        if os.path.exists(os.path.join(processed, f"{bug_id}{output_ext}")):
            log_callback(f"⏩ Skipped (Already Processed): {bug_id}\n")
            continue

        log_callback(f"🎬 Processing: {bug_id} ({'Image' if is_image else 'Video'})...\n")
        details = get_bug_details(bug_id, excel)
        process_file(os.path.join(raw, filename), bug_id, details, processed, linkedin, is_image=is_image)
        log_callback(f"✅ Finished: {bug_id}\n")
        processed_count += 1

    log_callback(f"\n🏁 Done! Successfully processed {processed_count} new files.\n")
    messagebox.showinfo("Success", f"Processing completed!\nProcessed {processed_count} new files.")

    # החזרת הכפתור למצב פעיל בסיום
    on_complete_callback()


# ==========================================
# מחלקת ממשק המשתמש (GUI Window)
# ==========================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QA Evidence Auto Watermark")
        self.geometry("700x580")
        self.resizable(False, False)

        # כותרת ראשית
        self.title_label = ctk.CTkLabel(self, text="🎬 Evidence Processing Engine",
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # פאנל הגדרות
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=30, fill="x")

        # --- שדה בחירת קובץ אקסל ---
        self.excel_label = ctk.CTkLabel(self.form_frame, text="Excel STD File:", font=ctk.CTkFont(weight="bold"))
        self.excel_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.excel_entry = ctk.CTkEntry(self.form_frame, width=400)
        self.excel_entry.insert(0, DEFAULT_EXCEL_FILE)
        self.excel_entry.grid(row=0, column=1, padx=10, pady=10)
        self.excel_btn = ctk.CTkButton(self.form_frame, text="Browse", width=80, command=self.browse_excel)
        self.excel_btn.grid(row=0, column=2, padx=10, pady=10)

        # --- שדה בחירת תיקיית RAW ---
        self.raw_label = ctk.CTkLabel(self.form_frame, text="Raw Folder:", font=ctk.CTkFont(weight="bold"))
        self.raw_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.raw_entry = ctk.CTkEntry(self.form_frame, width=400)
        self.raw_entry.insert(0, DEFAULT_RAW_FOLDER)
        self.raw_entry.grid(row=1, column=1, padx=10, pady=10)
        self.raw_btn = ctk.CTkButton(self.form_frame, text="Browse", width=80, command=self.browse_raw)
        self.raw_btn.grid(row=1, column=2, padx=10, pady=10)

        # --- שדה בחירת תיקיית Output ---
        self.proc_label = ctk.CTkLabel(self.form_frame, text="Output Folder:", font=ctk.CTkFont(weight="bold"))
        self.proc_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.proc_entry = ctk.CTkEntry(self.form_frame, width=400)
        self.proc_entry.insert(0, DEFAULT_PROCESSED_FOLDER)
        self.proc_entry.grid(row=2, column=1, padx=10, pady=10)
        self.proc_btn = ctk.CTkButton(self.form_frame, text="Browse", width=80, command=self.browse_processed)
        self.proc_btn.grid(row=2, column=2, padx=10, pady=10)

        # --- שדה טקסט חופשי ל-LinkedIn ---
        self.ln_label = ctk.CTkLabel(self.form_frame, text="Watermark Text:", font=ctk.CTkFont(weight="bold"))
        self.ln_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.ln_entry = ctk.CTkEntry(self.form_frame, width=400)
        self.ln_entry.insert(0, DEFAULT_LINKEDIN)
        self.ln_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        # כפתור הפעלה מרכזי
        self.start_btn = ctk.CTkButton(self, text="🚀 START PROCESSING EVIDENCE",
                                       font=ctk.CTkFont(size=16, weight="bold"), height=45, fg_color="green",
                                       hover_color="darkgreen", command=self.start_engine)
        self.start_btn.pack(pady=20)

        # חלון לוגים (Terminal פנימי בתוך האפליקציה)
        self.log_label = ctk.CTkLabel(self, text="Console Output:", font=ctk.CTkFont(weight="bold"))
        self.log_label.pack(anchor="w", padx=30)
        self.log_textbox = ctk.CTkTextbox(self, height=150, width=640, font=ctk.CTkFont(family="Courier"))
        self.log_textbox.pack(pady=5, padx=30)
        self.log_textbox.configure(state="disabled")

    def browse_excel(self):
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file:
            self.excel_entry.delete(0, ctk.END)
            self.excel_entry.insert(0, file)

    def browse_raw(self):
        folder = filedialog.askdirectory()
        if folder:
            self.raw_entry.delete(0, ctk.END)
            self.raw_entry.insert(0, folder)

    def browse_processed(self):
        folder = filedialog.askdirectory()
        if folder:
            self.proc_entry.delete(0, ctk.END)
            self.proc_entry.insert(0, folder)

    def log_message(self, message):
        """הדפסת טקסט לחלון הקונסול בממשק בצורה בטוחה"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(ctk.END, message)
        self.log_textbox.see(ctk.END)
        self.log_textbox.configure(state="disabled")

    def reset_button_state(self):
        """מחזיר את כפתור ההפעלה למצב רגיל"""
        self.start_btn.configure(state="normal", text="🚀 START PROCESSING EVIDENCE")

    def start_engine(self):
        excel = self.excel_entry.get()
        raw = self.raw_entry.get()
        processed = self.proc_entry.get()
        linkedin = self.ln_entry.get()

        # השבתת הכפתור למניעת לחיצות כפולות
        self.start_btn.configure(state="disabled", text="Processing... Please Wait")

        # הפעלת מנוע האוטומציה בתוך Thread נפרד כדי למנוע קפיאה של חלון ה-GUI
        threading.Thread(
            target=run_automation_engine,
            args=(excel, raw, processed, linkedin, self.log_message, self.reset_button_state),
            daemon=True
        ).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()