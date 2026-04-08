import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
from twilio.rest import Client

# --- 1. الإعدادات العامة (تعدل حسب بياناتك) ---
ADMIN_USER = "admin"
ADMIN_PASSWORD = "123123"

# بيانات Twilio - استبدلها ببياناتك من موقع Twilio Console
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxx' 
TWILIO_AUTH_TOKEN = 'your_auth_token_here'
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886' 
YOUR_WHATSAPP_NUMBER = 'whatsapp:+9665XXXXXXXX' 

DB_FILE = "tickets_db.csv"

# --- 2. الدوال المساعدة ---

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["ID", "Name", "Department", "Issue", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tickets')
    return output.getvalue()

def send_whatsapp_alert(ticket_id, name, dept, issue):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        body = f"🎫 *طلب دعم جديد*\n\n*رقم:* {ticket_id}\n*المرسل:* {name}\n*الموقع:* {dept}\n*المشكلة:* {issue}"
        client.messages.create(from_=TWILIO_WHATSAPP_FROM, body=body, to=YOUR_WHATSAPP_NUMBER)
        return True
    except:
        return False

# --- 3. بناء واجهة التطبيق ---

st.set_page_config(page_title="نظام الدعم الفني", layout="wide")
df = load_data()

# القائمة الجانبية (تمت إضافة key لتفادي خطأ التكرار)
st.sidebar.title("القائمة الرئيسية")
choice = st.sidebar.selectbox("اختر الواجهة", ["إرسال طلب جديد", "لوحة تحكم الدعم الفني"], key="main_nav")

# --- واجهة الموظف ---
if choice == "إرسال طلب جديد":
    st.header("📝 نموذج تقديم طلب دعم")
    with st.form("user_form", clear_on_submit=True):
        name = st.text_input("الاسم الكامل")
        dept = st.selectbox("الموقع", ["مستشفى الدرب العام"])
        issue = st.text_area("القسم")
        issue = st.text_area("وصف المشكلة بالتفصيل")
        submit = st.form_submit_button("إرسال الطلب")
        
        if submit:
            if name and issue:
                new_id = len(df) + 1001
                new_row = {
                    "ID": new_id, "Name": name, "Department": dept, 
                    "Issue": issue, "Status": "جديد", 
                    "Reply": "لا يوجد رد", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                
                # إرسال التنبيه
                with st.spinner('جاري إرسال تنبيه واتساب...'):
                    send_whatsapp_alert(new_id, name, dept, issue)
                
                st.success(f"✅ تم الإرسال! رقم الطلب: {new_id}")
            else:
                st.error("⚠️ يرجى تعبئة جميع الحقول")

# --- واجهة الدعم الفني ---
else:
    st.header("🛠️ لوحة تحكم فريق الدعم")
    
    # تسجيل الدخول
    with st.sidebar.expander("🔐 تسجيل دخول الإدارة", expanded=True):
        u = st.text_input("المستخدم")
        p = st.text_input("كلمة المرور", type="password")

    if u == ADMIN_USER and p == ADMIN_PASSWORD:
        st.success("تم تسجيل الدخول بنجاح")
        
        # خيارات التصدير
        col1, col2 = st.columns(2)
        with col1:
            excel_data = to_excel(df)
            st.download_button("📥 تحميل ملف Excel", data=excel_data, 
                             file_name=f"Tickets_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col2:
            if st.button("🖨️ وضع الطباعة (PDF)"):
                st.table(df)

        st.divider()

        # عرض وإدارة الطلبات
        if not df.empty:
            st.subheader("🔍 مراجعة الطلبات")
            search = st.text_input("ابحث عن طلب...")
            display_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
            st.dataframe(display_df, use_container_width=True)

            st.divider()
            
            # الرد على الطلبات
            pending = df[df['Status'] != "تم الحل"]['ID'].tolist()
            if pending:
                st.subheader("✍️ الرد على طلب معلق")
                sid = st.selectbox("اختر رقم الطلب", pending)
                r_text = st.text_area("الرد")
                status = st.selectbox("تحديث الحالة", ["قيد المعالجة", "تم الحل"])
                
                if st.button("تحديث وحفظ"):
                    idx = df[df['ID'] == sid].index
