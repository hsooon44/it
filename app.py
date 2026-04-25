import telebot
import requests
from telebot import types
import yt_dlp
import os
import time
import sqlite3
import ctypes

# --- إعدادات الهوية البرمجية للمهندس حسن ---
try:
    myappid = 'hassan.zuhayfi.megabot.v5.0' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

# --- الإعدادات الأساسية ---
API_TOKEN = '7607475672:AAEJCLDxHozjb2r-1yCzyKPZVos-Cer6nLo'
ADMIN_ID = 6884706957 
bot = telebot.TeleBot(API_TOKEN)

# الحقوق والإعدادات
DEV_CREDITS = "\n\n**المبرمج: المهندس حسن زحيفي**"
DISCLAIMER = "\n\n**⚠️ أنا بريء من أي استخدام سيئ لهذا البوت**"
DB_NAME = "bot_database.db"
TIKTOK_URL = "https://www.tiktok.com/@hsooon44"
SNAP_URL = "https://www.snapchat.com/add/hso-04"

# --- وظائف قاعدة البيانات (القلب النابض للبوت) ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # جدول المستخدمين (لحفظ الأسماء والزيارات)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        first_name TEXT, 
        join_date TEXT, 
        is_blocked INTEGER DEFAULT 0)''')
    # جدول التحميلات (لحفظ الروابط والمنصات)
    cursor.execute('''CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        platform TEXT, 
        url TEXT, 
        date TEXT)''')
    conn.commit()
    conn.close()

def log_user(m):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (user_id, username, first_name, join_date) 
                      VALUES (?, ?, ?, ?) ON CONFLICT(user_id) 
                      DO UPDATE SET username=excluded.username, first_name=excluded.first_name''',
                   (m.from_user.id, m.from_user.username, m.from_user.first_name, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def log_download(uid, platform, url):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO downloads (user_id, platform, url, date) VALUES (?, ?, ?, ?)',
                   (uid, platform, url, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

init_db()

# --- واجهة الأزرار ---
def get_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("تابعني تيك توك 🎵", url=TIKTOK_URL),
               types.InlineKeyboardButton("تابعني سناب شات 👻", url=SNAP_URL))
    return markup

# --- محرك التحميل العالمي ---
def download_universal(url, chat_id, status_id, platform):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video:
                bot.send_video(chat_id, video, caption=f"✅ من {platform}\n{DEV_CREDITS}", reply_markup=get_markup())
            os.remove(file_path)
            bot.delete_message(chat_id, status_id)
            log_download(chat_id, platform, url)
            return True
    except: return False

# --- أوامر الإدارة (للمطور حسن زحيفي) ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users'); u_count = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM downloads'); d_count = c.fetchone()[0]
        conn.close()
        msg = (f"📊 **لوحة التحكم - المهندس حسن**\n━━━━━━━━━━━━━━━\n"
               f"👥 المستخدمين: {u_count}\n📥 إجمالي الروابط المحملة: {d_count}\n━━━━━━━━━━━━━━━\n"
               f"📣 للإذاعة: `/broadcast النص`\n📥 للتقرير: `/export`\n🚫 للحظر: `/block ID`")
        bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace('/broadcast', '').strip()
        if not text: return bot.reply_to(message, "⚠️ يرجى كتابة النص بعد الأمر.")
        
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute('SELECT user_id FROM users'); users = c.fetchall()
        conn.close()
        
        bot.send_message(ADMIN_ID, f"🚀 جاري الإرسال لـ {len(users)} مستخدم...")
        s, f = 0, 0
        for (uid,) in users:
            try:
                bot.send_message(uid, f"📢 **إعلان هام من الإدارة:**\n\n{text}{DEV_CREDITS}", parse_mode='Markdown')
                s += 1
                time.sleep(0.1) # لتجنب حظر التلجرام للبوت
            except: f += 1
        bot.send_message(ADMIN_ID, f"✅ اكتملت الإذاعة!\nنجاح: {s} | فشل: {f}")

@bot.message_handler(commands=['export'])
def export_data(message):
    if message.from_user.id == ADMIN_ID:
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute('SELECT * FROM users'); users = c.fetchall()
        with open("users_report.txt", "w", encoding="utf-8") as f:
            for u in users: f.write(f"ID: {u[0]} | User: @{u[1]} | Name: {u[2]} | Joined: {u[3]}\n")
        with open("users_report.txt", "rb") as f:
            bot.send_document(ADMIN_ID, f, caption="✅ تقرير المشتركين الكامل.")
        os.remove("users_report.txt")

# --- معالجة الروابط ---
@bot.message_handler(func=lambda m: True)
def main_handler(message):
    log_user(message) # تسجيل الزيارة والاسم تلقائياً
    url = message.text
    platform = None
    if 'tiktok.com' in url: platform = "TikTok"
    elif 'instagram.com' in url: platform = "Instagram"
    elif 'twitter.com' in url or 'x.com' in url: platform = "X/Twitter"
    elif 'youtube.com' in url or 'youtu.be' in url: platform = "YouTube"
    
    if not platform: return

    status_msg = bot.reply_to(message, f"🔍 جاري التحميل من {platform}... ⏳")
    
    if platform == "TikTok":
        try:
            res = requests.post("https://www.tikwm.com/api/", data={'url': url}).json()
            if res.get('code') == 0:
                data = res['data']
                if 'images' in data:
                    bot.send_media_group(message.chat.id, [types.InputMediaPhoto(img) for img in data['images'][:10]])
                else:
                    bot.send_video(message.chat.id, data['play'], caption=f"✅ تم\n{DEV_CREDITS}")
                bot.delete_message(message.chat.id, status_msg.message_id)
                log_download(message.from_user.id, platform, url)
                return
        except: pass

    if not download_universal(url, message.chat.id, status_msg.message_id, platform):
        bot.edit_message_text("❌ فشل التحميل. تأكد أن الرابط عام.", message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['start'])
def welcome(message):
    log_user(message)
    bot.reply_to(message, f"👋 أهلاً المهندس {message.from_user.first_name}\nأرسل أي رابط للتحميل فوراً.", reply_markup=get_markup())

    
def resource_path(relative_path):
    """ الحصول على المسار المطلق للموارد (يعمل في التطوير وفي EXE) """
    try:
        # PyInstaller ينشئ مجلد مؤقت ويخزن المسار في _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# الآن نستخدمها لجلب الأيقونة
icon_path = resource_path("logo.png")

if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("🚀 بوت المهندس حسن زحيفي V5.0 قيد التشغيل...")
    bot.infinity_polling()
