import ctypes
import sys
import os
import customtkinter as ctk
from flask import Flask, request, render_template_string
import threading
from plyer import notification
from datetime import datetime
import pandas as pd
import arabic_reshaper
from bidi.algorithm import get_display
import socket
import winreg as reg

# 1. إعطاء البرنامج هوية رسمية لويندوز (لظهور الإشعارات بعد التحويل لـ EXE)
def apply_windows_fix():
    try:
        my_app_id = 'company.maintenance.system.v2' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
    except Exception:
        pass

apply_windows_fix()

app = Flask(__name__)
gui_app = None
EXCEL_FILE = "Maintenance_Requests.xlsx"

# وظيفة إصلاح عرض النص العربي للواجهة الرسومية
def fix_text(text):
    if not text: return ""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# إضافة البرنامج للتشغيل التلقائي مع بدء الويندوز
def add_to_startup():
    try:
        pth = os.path.realpath(sys.executable)
        key = reg.HKEY_CURRENT_USER
        key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
        open_reg = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_reg, "Maintenance_Support_System", 0, reg.REG_SZ, pth)
        reg.CloseKey(open_reg)
    except Exception:
        pass

# --- صفحة الجوال المحدثة بنظام تبديل اللغات (AR/EN) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl" id="mainHtml">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="pageTitle">إرسال بلاغ صيانة</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; background-color: #f0f2f5; padding: 20px; text-align: center; transition: 0.3s; }
        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 450px; margin: auto; position: relative; }
        .lang-btn { position: absolute; top: 15px; left: 15px; background: #f0f2f5; border: 1px solid #ddd; padding: 5px 12px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold; color: #1a73e8; }
        [dir="ltr"] .lang-btn { left: auto; right: 15px; }
        h2 { color: #1a73e8; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; font-size: 16px; box-sizing: border-box; text-align: inherit; }
        button#submitBtn { width: 100%; background-color: #1a73e8; color: white; padding: 18px; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 10px; }
        button:active { background-color: #1557b0; transform: scale(0.98); }
    </style>
</head>
<body>
    <div class="card">
        <button type="button" class="lang-btn" onclick="toggleLang()" id="langSwitcher">English</button>
        <h2 id="h2_title">نظام البلاغات الإلكتروني</h2>
        <p id="p_sub" style="color: #666; margin-bottom: 20px;">E-Health Maintenance System</p>
        
        <form action="/post_issue" method="post" onsubmit="return handleFormSubmit();">
            <input type="text" name="name" id="nameInput" placeholder="الاسم الكامل" required>
            <input type="text" name="emp_id" id="idInput" placeholder="الرقم الوظيفي" required>
            <input type="email" name="email" id="emailInput" placeholder="البريد الإلكتروني" required>
            <select name="loc" id="locSelect">
                <option value="الاداره">الاداره / Administration</option>
                <option value="التمريض">التمريض / Nursing</option>
                <option value="قسم الطوارى">قسم الطوارى / ER</option>
                <option value="قسم العيادات">قسم العيادات / Clinics</option>
                <option value="قسم المختبر">قسم المختبر / Laboratory</option>
                <option value="أخر">أخر / Other</option>
            </select>
            <textarea name="issue" id="issueInput" rows="4" placeholder="وصف المشكلة..." required></textarea>
            <button type="submit" id="submitBtn">إرسال البلاغ</button>
        </form>
    </div>

    <script>
        let currentLang = 'ar';
        const trans = {
            ar: {
                title: "إرسال بلاغ صيانة",
                h2: "نظام البلاغات الإلكتروني",
                sub: "قسم الصيانة والدعم الفني",
                name: "الاسم الكامل",
                id: "الرقم الوظيفي",
                email: "البريد الإلكتروني",
                issue: "وصف المشكلة...",
                btn: "إرسال البلاغ",
                switch: "English",
                alert: "جاري الإرسال... شكراً لك."
            },
            en: {
                title: "Maintenance Request",
                h2: "Electronic Request System",
                sub: "Maintenance & Tech Support Dept",
                name: "Full Name",
                id: "Employee ID",
                email: "Email Address",
                issue: "Describe the issue...",
                btn: "Send Request",
                switch: "العربية",
                alert: "Sending... Thank you."
            }
        };

        function toggleLang() {
            currentLang = currentLang === 'ar' ? 'en' : 'ar';
            const dir = currentLang === 'ar' ? 'rtl' : 'ltr';
            document.getElementById('mainHtml').dir = dir;
            document.getElementById('mainHtml').lang = currentLang;
            
            document.getElementById('pageTitle').innerText = trans[currentLang].title;
            document.getElementById('h2_title').innerText = trans[currentLang].h2;
            document.getElementById('p_sub').innerText = trans[currentLang].sub;
            document.getElementById('nameInput').placeholder = trans[currentLang].name;
            document.getElementById('idInput').placeholder = trans[currentLang].id;
            document.getElementById('emailInput').placeholder = trans[currentLang].email;
            document.getElementById('issueInput').placeholder = trans[currentLang].issue;
            document.getElementById('submitBtn').innerText = trans[currentLang].btn;
            document.getElementById('langSwitcher').innerText = trans[currentLang].switch;
        }

        function handleFormSubmit() {
            if ("vibrate" in navigator) { navigator.vibrate([200, 100, 200]); }
            alert(trans[currentLang].alert);
            return true;
        }
    </script>
</body>
</html>
"""

class SupportDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Support Control Panel - لوحة تحكم الدعم")
        self.geometry("800x800")
        self.current_lang = "ar"

        self.translations = {
            "ar": {
                "header": fix_text("سجل البلاغات"),
                "switch": "English",
                "status": fix_text("الحالة: متصل وجاهز"),
                "url_text": "رابط الجوال: ",
                "notif_title": "🚨 بلاغ جديد مستلم",
                "labels": {"date": "📅 التاريخ: ", "time": "⏰ الوقت: ", "name": "👤 الاسم: ", "id": "🆔 الرقم: ", "email": "📧 ايميل: ", "dept": "📍 القسم: ", "issue": "🛠️ المشكله: "}
            },
            "en": {
                "header": "Organized Request Log",
                "switch": "العربية",
                "status": "Status: Connected & Ready",
                "url_text": "Mobile Link: ",
                "notif_title": "🚨 New Request Received",
                "labels": {"date": "📅 Date: ", "time": "⏰ Time: ", "name": "👤 Name: ", "id": "🆔 ID: ", "email": "📧 Email: ", "dept": "📍 Dept: ", "issue": "🛠️ Issue: "}
            }
        }

        self.lang_btn = ctk.CTkButton(self, text=self.translations["ar"]["switch"], width=100, command=self.toggle_language)
        self.lang_btn.pack(pady=10, padx=20, anchor="ne")

        self.header_label = ctk.CTkLabel(self, text=self.translations["ar"]["header"], font=("Arial", 24, "bold"), text_color="#1a73e8")
        self.header_label.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, width=750, height=480, font=("Arial", 16), border_width=2)
        self.log_box.pack(pady=10, padx=20)

        self.local_ip = self.get_ip()
        self.url_label = ctk.CTkLabel(self, text=f"{self.translations['ar']['url_text']} http://{self.local_ip}:8787", font=("Arial", 14, "bold"), text_color="#d35400")
        self.url_label.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text=self.translations["ar"]["status"], text_color="#27ae60")
        self.status_label.pack(pady=5)

    def get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return socket.gethostbyname(socket.gethostname())

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        lang = self.current_lang
        self.header_label.configure(text=self.translations[lang]["header"])
        self.lang_btn.configure(text=self.translations[lang]["switch"])
        self.status_label.configure(text=self.translations[lang]["status"])
        self.url_label.configure(text=f"{self.translations[lang]['url_text']} http://{self.local_ip}:8787")

    def save_to_excel(self, data_dict):
        try:
            ordered_columns = ["التاريخ", "الوقت", "الاسم", "الرقم الوظيفي", "الايميل", "القسم", "المشكله"]
            df_new = pd.DataFrame([data_dict])[ordered_columns]
            if not os.path.isfile(EXCEL_FILE):
                df_new.to_excel(EXCEL_FILE, index=False)
            else:
                try:
                    existing_df = pd.read_excel(EXCEL_FILE)
                    pd.concat([existing_df, df_new], ignore_index=True).to_excel(EXCEL_FILE, index=False)
                except PermissionError:
                    print("⚠️ الملف مفتوح حالياً.")
        except Exception as e:
            print(f"Excel Error: {e}")

    def update_ui_with_data(self, data):
        now_date = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%I:%M %p")
        lang = self.current_lang
        lbl = self.translations[lang]["labels"]
        is_ar = (lang == "ar")

        entry_text = (
            f"{lbl['date']} {now_date}\n"
            f"{lbl['time']} {now_time}\n"
            f"{lbl['name']} {fix_text(data['name']) if is_ar else data['name']}\n"
            f"{lbl['id']} {data.get('emp_id', 'N/A')}\n"
            f"{lbl['dept']} {fix_text(data['loc']) if is_ar else data['loc']}\n"
            f"{lbl['issue']} {fix_text(data['issue']) if is_ar else data['issue']}\n"
            f"{'━' * 55}\n"
        )
        self.log_box.insert("1.0", entry_text)
        
        excel_data = {
            "التاريخ": now_date, "الوقت": now_time, "الاسم": data['name'], 
            "الرقم الوظيفي": data.get('emp_id', ''), "الايميل": data.get('email', ''), 
            "القسم": data['loc'], "المشكله": data['issue']
        }
        self.save_to_excel(excel_data)
        
        try:
            notification.notify(
                title=self.translations[lang]["notif_title"], 
                message=f"{data['name']} - {data['loc']}", 
                app_name="Maintenance System",
                timeout=10
            )
        except Exception:
            pass

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/post_issue', methods=['POST'])
def receive():
    data = request.form.to_dict()
    if gui_app and data:
        gui_app.after(100, lambda: gui_app.update_ui_with_data(data))
    return "<h1 style='text-align:center; color:#1a73e8; font-family:sans-serif;'>تم الإرسال بنجاح!</h1>"

def run_server():
    app.run(host='0.0.0.0', port=8787, debug=False, use_reloader=False)

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        add_to_startup()
        
    gui_app = SupportDashboard()
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    gui_app.mainloop()
