import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# --- 1. الإعدادات وقاعدة البيانات ---
DB_FILE = "tickets_db.csv"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "Dit@123123"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype=str).fillna("")
    return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueType", "IssueDesc", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Support System", layout="centered")

# --- 3. نظام أزرار تغيير اللغة (الضغط المباشر) ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'AR'

st.sidebar.markdown("### 🌐 Language / اللغة")
# إنشاء زرين بجانب بعضهما للتبديل السريع
col_lang_ar, col_lang_en = st.sidebar.columns(2)

if col_lang_ar.button("AR | العربية", use_container_width=True):
    st.session_state.lang = 'AR'
    st.rerun()

if col_lang_en.button("EN | English", use_container_width=True):
    st.session_state.lang = 'EN'
    st.rerun()

L = st.session_state.lang

# نصوص الواجهة بناءً على اللغة المختارة
t = {
    'AR': {
        'title': "نظام الدعم الفني", 'sub': "يرجى تعبئة النموذج أدناه"،
        'name': "👤 الاسم الكامل", 'id': "🆔 الرقم الوظيفي", 'email': "📧 البريد الإلكتروني",
        'dept': "🏢 القسم", 'type': "⚠️ نوع المشكلة", 'desc': "📝 وصف المشكلة بالتفصيل",
        'submit': "إرسال الطلب", 'dir': "rtl", 'align': "right", 'user_tab': "طلب دعم جديد", 
        'admin_tab': "لوحة الإدارة", 'success': "✅ تم الإرسال بنجاح!", 'error': "⚠️ يرجى تعبئة الحقول الأساسية"
    },
    'EN': {
        'title': "Technical Support", 'sub': "Please fill out the form below",
        'name': "👤 Full Name", 'id': "🆔 Employee ID", 'email': "📧 Email",
        'dept': "🏢 Department", 'type': "⚠️ Issue Type", 'desc': "📝 Issue Description",
        'submit': "Submit Request", 'dir': "ltr", 'align': "left", 'user_tab': "New Ticket",
        'admin_tab': "Admin Dashboard", 'success': "✅ Submitted Successfully!", 'error': "⚠️ Please fill required fields"
    }
}

# --- 4. CSS المتقدم للواجهة المتجاوبة ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[L]['dir']};
        background-color: #f4f7f9;
    }}

    /* تصميم النموذج كبطاقة */
    [data-testid="stForm"] {{
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: none;
    }}

    /* تنسيق الأزرار لتكون مناسبة للمس في الجوال */
    .stButton>button {{
        border-radius: 10px !important;
        height: 3.5em !important;
        font-weight: bold !important;
        width: 100% !important;
    }}

    /* حقول الإدخال */
    input, textarea, [data-baseweb="select"] {{
        text-align: {t[L]['align']} !important;
        border-radius: 8px !important;
    }}

    /* إخفاء شعار ستريم ليت المزعج في الجوال */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 5. التنقل (المنيو) ---
st.sidebar.divider()
choice = st.sidebar.radio(
    "القائمة" if L == 'AR' else "Menu",
    [t[L]["user_tab"], t[L]["admin_tab"]]
)

# --- 6. واجهة المستخدم ---
if choice == t[L]["user_tab"]:
    st.markdown(f"<h1 style='text-align: center; color: #2c3e50;'>{t[L]['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #7f8c8d;'>{t[L]['sub']}</p>", unsafe_allow_html=True)
    
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(t[L]["name"])
            empid = st.text_input(t[L]["id"])
        with col2:
            email = st.text_input(t[L]["email"])
            dept = st.text_input(t[L]["dept"])
        
        issue_type = st.selectbox(t[L]["type"], ["Hardware", "Software", "Network", "Other"] if L == 'EN' else ["أجهزة", "أنظمة", "شبكات", "أخرى"])
        issue_desc = st.text_area(t[L]["desc"])
        
        if st.form_submit_button(t[L]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc, "Status": "New" if L == 'EN' else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"{t[L]['success']} ID: {new_id}")
            else:
                st.error(t[L]["error"])

# --- 7. واجهة الإدارة ---
else:
    st.markdown(f"<h1 style='text-align: center;'>{t[L]['admin_tab']}</h1>", unsafe_allow_html=True)
    with st.sidebar.expander("🔐 Admin Login"):
        admin_user = st.text_input("User")
        admin_pass = st.text_input("Pass", type="password")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Download Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)
    else:
        st.info("الرجاء تسجيل الدخول" if L == 'AR' else "Please login to continue")
