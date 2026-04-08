import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الحماية ---
ADMIN_USER = "admin"      # اسم المستخدم لوحة الدعم
ADMIN_PASSWORD = "123123"    # كلمة المرور لوحة الدعم

# إعداد ملف البيانات
DB_FILE = "tickets_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["ID", "Name", "Department", "Issue", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

st.set_page_config(page_title="نظام الدعم الفني", layout="wide")
st.title("🎫 نظام الدعم الفني الذكي")

menu = ["إرسال طلب جديد", "لوحة تحكم الدعم الفني"]
choice = st.sidebar.selectbox("اختر الواجهة", menu)

df = load_data()

# --- 1. واجهة الموظف (بدون باسورد) ---
if choice == "إرسال طلب جديد":
    st.header("📝 تقديم طلب دعم")
    with st.form("ticket_form"):
        name = st.text_input("الاسم الكامل")
        dept = st.selectbox("الموقع", ["مستشفى الدرب العام"])
        issue = st.text_area("القسم")
        issue = st.text_area("وصف المشكلة")
        submit = st.form_submit_button("إرسال الطلب")

        if submit:
            if name and issue:
                new_id = len(df) + 1001
                new_row = {
                    "ID": new_id, "Name": name, "Department": dept, 
                    "Issue": issue, "Status": "جديد", 
                    "Reply": "لا يوجد رد بعد", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"تم إرسال طلبك! رقم الطلب: {new_id}")
            else:
                st.error("يرجى تعبئة جميع الحقول.")

# --- 2. واجهة الدعم الفني (تحتاج يوزر وباسورد) ---
else:
    st.header("🛠️ تسجيل دخول فريق الدعم")
    
    # نموذج تسجيل الدخول
    with st.sidebar.expander("قفل الأمان", expanded=True):
        user = st.text_input("اسم المستخدم")
        passwd = st.text_input("كلمة المرور", type="password")
    
    if user == ADMIN_USER and passwd == ADMIN_PASSWORD:
        st.success("تم تسجيل الدخول بنجاح ✅")
        
        if df.empty:
            st.info("لا توجد طلبات حالياً.")
        else:
            st.subheader("الطلبات الواردة")
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.subheader("الرد على الطلبات")
            
            # فلترة الطلبات التي لم تحل بعد
            pending_tickets = df[df['Status'] != "تم الحل"]['ID'].tolist()
            
            if pending_tickets:
                selected_id = st.selectbox("اختر رقم الطلب للرد عليه", pending_tickets)
                reply_text = st.text_area("اكتب الرد الفني هنا")
                new_status = st.selectbox("تحديث الحالة", ["قيد المعالجة", "تم الحل"])
                
                if st.button("تحديث وحفظ"):
                    idx = df[df['ID'] == selected_id].index[0]
                    df.at[idx, 'Reply'] = reply_text
                    df.at[idx, 'Status'] = new_status
                    save_data(df)
                    st.success(f"تم تحديث الطلب {selected_id}")
                    st.rerun()
            else:
                st.balloons()
                st.success("عمل رائع! تم إنجاز جميع المهام.")
    
    elif user != "" or passwd != "":
        st.error("اسم المستخدم أو كلمة المرور غير صحيحة ❌")
    else:
        st.warning("يرجى إدخال بيانات الدخول في القائمة الجانبية للوصول للوحة التحكم.")
