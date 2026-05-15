import os
import pandas as pd
import textwrap
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip, ImageClip

# הגדרת ImageMagick
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

LINKEDIN_URL = "www.linkedin.com/in/Meir-Yaakovi"
RAW_FOLDER = "Evidence/Raw"
PROCESSED_FOLDER = "Evidence/Processed"
EXCEL_FILE = "MyProject/STD.xlsx"

SEVERITY_COLORS = {
    "Show Stop": "red",
    "Critical": "darkred",
    "Major": "orange",
    "Moderate": "yellow",
    "Low": "green"
}

os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def wrap_text(text, width):
    if not text or text == "N/A":
        return text
    wrapper = textwrap.TextWrapper(width=width, break_long_words=False, replace_whitespace=False)
    return "\n".join(wrapper.wrap(text))


def get_bug_details(bug_id):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="NetflixSTD", engine='openpyxl')
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


def process_file(file_path, bug_id, details, is_image=False):
    print(f"🎬 מעבד את {'תמונת' if is_image else 'באג'}: {bug_id}")
    try:
        # טעינת המקור (וידאו או תמונה)
        if is_image:
            source = ImageClip(file_path)
        else:
            source = VideoFileClip(file_path)

        w, h = source.size
        severity = details['severity'] if details else "N/A"
        summary = details['summary'] if details else "N/A"
        category = details['category'] if details else "N/A"
        sev_color = SEVERITY_COLORS.get(severity, "white")

        # הגדרות רזולוציה
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

        # --- וואטרמארק ---
        wm_content = (f"{bug_id} | {severity} | {category}\n"
                      f"{wrapped_summary}\n"
                      f"{LINKEDIN_URL}\n\n.")

        watermark = TextClip(text=wm_content, font_size=wm_fs, color=sev_color,
                             method='label', interline=5).with_opacity(0.8)

        # התאמת משך הזמן של הוואטרמארק (לתמונות זה לא משנה אבל MoviePy דורש)
        watermark = watermark.with_duration(source.duration if not is_image else 1)

        wm_h = watermark.h
        dynamic_y = h - wm_h - margin_y
        final_wm = watermark.with_position((pos_x, dynamic_y))

        # שילוב הוואטרמארק
        combined = CompositeVideoClip([source, final_wm])

        if is_image:
            # שמירה כתמונה
            output_path = os.path.join(PROCESSED_FOLDER, f"{bug_id}.png")
            combined.save_frame(output_path)  # שומר פריים בודד כתמונה
            print(f"✅ תמונה נשמרה: {output_path}")
        else:
            # המשך הלוגיקה של הוידאו (שקופית פתיחה + שילוב)
            intro_fs = h // 35 if w < h else h // 25
            intro_content = (f"ID: {bug_id}\n\nCategory:\n{wrapped_category}\n\n"
                             f"Summary:\n{wrapped_summary}\n\nSeverity: {severity}\n\n"
                             f"Date: {details['date']}\n\n{LINKEDIN_URL}\n\n.")

            bg_intro = ColorClip(size=(w, h), color=(0, 0, 0)).with_duration(5)
            txt_intro = TextClip(text=intro_content, font_size=intro_fs, color=sev_color,
                                 method='label', interline=10).with_duration(5)

            intro = CompositeVideoClip([bg_intro, txt_intro.with_position('center')])
            final = concatenate_videoclips([intro, combined])

            output_path = os.path.join(PROCESSED_FOLDER, f"{bug_id}.mp4")
            final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        source.close()

    except Exception as e:
        print(f"❌ שגיאה ב-{bug_id}: {e}")


def main():
    if not os.path.exists(RAW_FOLDER): return
    for filename in os.listdir(RAW_FOLDER):
        ext = os.path.splitext(filename)[1].lower()
        if filename.startswith('.'): continue

        bug_id = os.path.splitext(filename)[0]
        is_video = ext in ('.mp4', '.mov')
        is_image = ext in ('.png', '.jpg', '.jpeg')

        if not (is_video or is_image): continue

        # בדיקה אם כבר עובד
        output_ext = ".mp4" if is_video else ".png"
        if os.path.exists(os.path.join(PROCESSED_FOLDER, f"{bug_id}{output_ext}")):
            print(f"⏩ מדלג על {bug_id}")
            continue

        details = get_bug_details(bug_id)
        process_file(os.path.join(RAW_FOLDER, filename), bug_id, details, is_image=is_image)


if __name__ == "__main__":
    main()