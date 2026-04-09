import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# --- 1. الإعدادات وقاعدة البيانات ---
DB_FILE = "tickets_db.csv"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "123123"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueType", "IssueDesc", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- 2. إعدادات الصفحة واللغة ---
st.set_page_config(page_title="Support System | نظام الدعم", layout="wide")

lang = st.sidebar.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English"])

t = {
    "العربية": {
        "title": "طلب الدعم الفني",
        "subtitle": "يرجى تعبئة النموذج أدناه وسيتم الرد عليكم في أقرب وقت",
        "name": "👤 الاسم الكامل",
        "empid": "🆔 الرقم الوظيفي",
        "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم (كتابة)",
        "type": "⚠️ نوع المشكلة",
        "desc": "📝 وصف المشكلة بالتفصيل",
        "submit": "إرسال الطلب",
        "admin_tab": "لوحة الإدارة",
        "user_tab": "طلب دعم جديد",
        "success": "✅ تم إرسال طلبك بنجاح!",
        "error": "⚠️ يرجى ملء كافة الحقول",
        "login": "🔐 تسجيل دخول المشرف",
        "search": "🔍 بحث...",
        "delete_one": "🗑️ حذف طلب محدد",
        "delete_all": "🚨 حذف جميع الطلبات",
        "confirm_del": "هل أنت متأكد من الحذف؟",
        "dir": "rtl", "align": "right"
    },
    "English": {
        "title": "Technical Support Request",
        "subtitle": "Please fill out the form below",
        "name": "👤 Full Name",
        "empid": "🆔 Employee ID",
        "email": "📧 Email Address",
        "dept": "🏢 Department",
        "type": "⚠️ Issue Type",
        "desc": "📝 Description",
        "submit": "Submit Request",
        "admin_tab": "Admin Dashboard",
        "user_tab": "New Ticket",
        "success": "✅ Submitted successfully!",
        "error": "⚠️ Please fill all fields",
        "login": "🔐 Admin Login",
        "search": "🔍 Search...",
        "delete_one": "🗑️ Delete Specific Ticket",
        "delete_all": "🚨 Delete All Tickets",
        "confirm_del": "Are you sure you want to delete?",
        "dir": "ltr", "align": "left"
    }
}

# --- 3. تصميم الواجهة ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; direction: {t[lang]['dir']}; text-align: {t[lang]['align']}; }}
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #4361ee; color: white; }}
    .btn-danger>button {{ background-color: #e63946 !important; }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 4. القائمة الجانبية ---
choice = st.sidebar.radio("Menu", [t[lang]["user_tab"], t[lang]["admin_tab"]])

# --- 5. واجهة المستخدم ---
if choice == t[lang]["user_tab"]:
    st.markdown(f"<h1 style='text-align: center; color: #4361ee;'>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name, empid, email = st.text_input(t[lang]["name"]), st.text_input(t[lang]["empid"]), st.text_input(t[lang]["email"])
        with col2:
            dept = st.text_input(t[lang]["dept"])
            issue_type = st.selectbox(t[lang]["type"], ["Hardware", "Software", "Network", "Other"] if lang=="English" else ["أجهزة", "أنظمة", "شبكات", "أخرى"])
        issue_desc = st.text_area(t[lang]["desc"])
        if st.form_submit_button(t[lang]["submit"]):
            if name and empid and dept:
                new_row = {"ID": len(df)+1001, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc, "Status": "New" if lang=="English" else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(t[lang]["success"])
            else: st.error(t[lang]["error"])

# --- 6. واجهة الإدارة (مع ميزة الحذف) ---
else:
    st.markdown(f"<h1 style='text-align: center;'>{t[lang]['admin_tab']}</h1>", unsafe_allow_html=True)
    with st.sidebar.expander(t[lang]["login"]):
        admin_user, admin_pass = st.text_input("User"), st.text_input("Pass", type="password")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.subheader("🗑️ " + ("Data Management" if lang=="English" else "إدارة وحذف البيانات"))
        
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            # حذف طلب واحد عن طريق ID
            st.markdown(f"**{t[lang]['delete_one']}**")
            ticket_to_del = st.selectbox("Select ID", df['ID'].tolist() if not df.empty else [None])
            if st.button("🗑️ " + ("Delete Selected" if lang=="English" else "حذف الطلب المختار"), key="del_one"):
                if ticket_to_del:
                    df = df[df['ID'] != ticket_to_del]
                    save_data(df)
                    st.warning(f"Ticket {ticket_to_del} Deleted!")
                    st.rerun()

        with col_del2:
            # حذف الكل (تحديد الكل)
            st.markdown(f"**{t[lang]['delete_all']}**")
            confirm = st.checkbox(t[lang]["confirm_del"])
            if st.button("🔥 " + ("Clear All Data" if lang=="English" else "مسح كافة البيانات"), key="del_all"):
                if confirm:
                    df = pd.DataFrame(columns=df.columns)
                    save_data(df)
                    st.success("All Data Cleared!")
                    st.rerun()
                else:
                    st.error("Please confirm first / يرجى التأكيد أولاً")
                    
    else:
        st.warning("Please login / يرجى تسجيل الدخول")
