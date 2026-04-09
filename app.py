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
        # إضافة dtype=str لمنع أخطاء TypeError عند النشر
        return pd.read_csv(DB_FILE, dtype=str).fillna("")
    else:
        return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueType", "IssueDesc", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    # تحويل البيانات إلى Excel مع التأكد من حفظها كقيم نصية
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
        "success": "✅ تم إرسال طلبك بنجاح! رقم المتابعة: ",
        "error": "⚠️ يرجى ملء كافة الحقول الأساسية",
        "login": "🔐 تسجيل دخول المشرف",
        "user_field": "اسم المستخدم",
        "pass_field": "كلمة المرور",
        "stats_total": "إجمالي الطلبات",
        "stats_pending": "تحت المعالجة",
        "stats_done": "تم الحل",
        "search": "🔍 بحث في الطلبات...",
        "reply_btn": "تحديث الحالة والرد",
        "delete_section": "🗑️ إدارة وحذف البيانات",
        "del_btn": "حذف الطلب المختار",
        "del_all_btn": "🗑️ حذف كافة البيانات (تحديد الكل)",
        "confirm_all": "أؤكد رغبتي في مسح جميع البيانات نهائياً",
        "dir": "rtl", "align": "right"
    },
    "English": {
        "title": "Technical Support Request",
        "subtitle": "Please fill out the form below and we will respond shortly",
        "name": "👤 Full Name",
        "empid": "🆔 Employee ID",
        "email": "📧 Email Address",
        "dept": "🏢 Department (Type here)",
        "type": "⚠️ Issue Type",
        "desc": "📝 Detailed Issue Description",
        "submit": "Submit Request",
        "admin_tab": "Admin Dashboard",
        "user_tab": "New Ticket",
        "success": "✅ Submitted successfully! Ticket ID: ",
        "error": "⚠️ Please fill all required fields",
        "login": "🔐 Admin Login",
        "user_field": "Username",
        "pass_field": "Password",
        "stats_total": "Total Tickets",
        "stats_pending": "Pending",
        "stats_done": "Resolved",
        "search": "🔍 Search Tickets...",
        "reply_btn": "Update & Reply",
        "delete_section": "🗑️ Data Management & Deletion",
        "del_btn": "Delete Selected Ticket",
        "del_all_btn": "🗑️ Delete All Data (Select All)",
        "confirm_all": "I confirm that I want to permanently delete all data",
        "dir": "ltr", "align": "left"
    }
}

# --- 3. تصميم الواجهة (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[lang]['dir']};
        text-align: {t[lang]['align']};
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        background-color: #4361ee;
        color: white;
        font-weight: bold;
    }}
    /* زر الحذف بلون أحمر */
    div[data-testid="stButton"] button:contains("حذف"), 
    div[data-testid="stButton"] button:contains("Delete") {{
        background-color: #ef233c !important;
    }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 4. القائمة الجانبية ---
choice = st.sidebar.radio(f"{'Menu' if lang=='English' else 'القائمة'}", [t[lang]["user_tab"], t[lang]["admin_tab"]])

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
            if name and empid and dept and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc, "Status": "New" if lang=="English" else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"{t[lang]['success']} {new_id}")
            else: st.error(t[lang]["error"])

# --- 6. واجهة الإدارة ---
else:
    st.markdown(f"<h1 style='text-align: center;'>{t[lang]['admin_tab']}</h1>", unsafe_allow_html=True)
    with st.sidebar.expander(t[lang]["login"]):
        admin_user, admin_pass = st.text_input(t[lang]["user_field"]), st.text_input(t[lang]["pass_field"], type="password")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        # إحصائيات
        c1, c2, c3 = st.columns(3)
        c1.metric(t[lang]["stats_total"], len(df))
        c2.metric(t[lang]["stats_pending"], len(df[df['Status'].isin(["New", "جديد", "Pending", "قيد المعالجة"])]))
        c3.metric(t[lang]["stats_done"], len(df[df['Status'].isin(["Resolved", "تم الحل"])]))
        
        st.divider()
        col_search, col_export = st.columns([3, 1])
        with col_search: search = st.text_input(t[lang]["search"])
        with col_export: 
            st.write(" ")
            st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx")

        display_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(display_df, use_container_width=True)

        # --- قسم الرد والحذف الجديد ---
        st.markdown("---")
        col_action, col_delete = st.columns(2)

        with col_action:
            st.subheader(f"{'Process Ticket' if lang=='English' else 'معالجة الطلبات'}")
            all_ids = df['ID'].tolist()
            if all_ids:
                selected_id = st.selectbox("Ticket ID", all_ids, key="process_id")
                reply_text = st.text_area(f"{'Official Reply' if lang=='English' else 'الرد الرسمي'}")
                status_options = ["Resolved", "Pending"] if lang == "English" else ["تم الحل", "قيد المعالجة"]
                new_status = st.selectbox(t[lang]["type"], status_options, key="status_select")
                if st.button(t[lang]["reply_btn"]):
                    # استخدام iloc لتجنب أخطاء النوع Dtype Mismatch
                    idx = df[df['ID'] == str(selected_id)].index[0]
                    df.iloc[idx, df.columns.get_loc('Reply')] = str(reply_text)
                    df.iloc[idx, df.columns.get_loc('Status')] = str(new_status)
                    save_data(df)
                    st.success("Updated!")
                    st.rerun()

        with col_delete:
            st.subheader(t[lang]["delete_section"])
            # 1. حذف طلب واحد
            del_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="del_id")
            if st.button(t[lang]["del_btn"]):
                if del_id:
                    df = df[df['ID'] != str(del_id)]
                    save_data(df)
                    st.warning(f"Ticket {del_id} Deleted!")
                    st.rerun()
            
            st.divider()
            # 2. حذف الكل (تحديد الكل)
            st.markdown(f"⚠️ **{t[lang]['del_all_btn']}**")
            confirm_del = st.checkbox(t[lang]["confirm_all"])
            if st.button(t[lang]["del_all_btn"]):
                if confirm_del:
                    df = pd.DataFrame(columns=df.columns)
                    save_data(df)
                    st.success("All data wiped!")
                    st.rerun()
                else:
                    st.error("Please confirm check-box first!")
    else:
        if admin_user or admin_pass:
            st.error("Wrong credentials!")
        st.warning("Please login from sidebar")
