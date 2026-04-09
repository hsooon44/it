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
    else:
        return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueType", "IssueDesc", "Status", "Reply", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Support System", layout="wide")

# نظام اختيار اللغة في الأعلى
if 'lang_choice' not in st.session_state:
    st.session_state.lang_choice = "العربية"

# سطر علوي لاختيار اللغة
l_col1, l_col2 = st.columns([8, 1])
with l_col2:
    current_lang = st.selectbox("🌐", ["العربية", "English"], label_visibility="collapsed")
    st.session_state.lang_choice = current_lang

lang = st.session_state.lang_choice

t = {
    "العربية": {
        "title": "طلب الدعم الفني",
        "subtitle": "يرجى تعبئة النموذج أدناه وسيتم الرد عليكم في أقرب وقت",
        "name": "👤 الاسم الكامل", "empid": "🆔 الرقم الوظيفي", "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم (كتابة)", "type": "⚠️ نوع المشكلة", "desc": "📝 وصف المشكلة بالتفصيل",
        "submit": "إرسال الطلب", "admin_tab": "لوحة الإدارة", "user_tab": "طلب دعم جديد",
        "success": "✅ تم الإرسال! رقم المتابعة: ", "error": "⚠️ يرجى ملء كافة الحقول",
        "login": "🔐 تسجيل دخول المشرف", "user_field": "اسم المستخدم", "pass_field": "كلمة المرور",
        "stats_total": "إجمالي الطلبات", "stats_pending": "تحت المعالجة", "stats_done": "تم الحل",
        "search": "🔍 بحث...", "reply_btn": "تحديث الحالة والرد", "del_btn": "حذف الطلب",
        "del_all_btn": "🗑️ حذف الكل", "confirm_all": "تأكيد المسح النهائي", "dir": "rtl", "align": "right"
    },
    "English": {
        "title": "Technical Support",
        "subtitle": "Please fill out the form below",
        "name": "👤 Full Name", "empid": "🆔 Employee ID", "email": "📧 Email Address",
        "dept": "🏢 Department", "type": "⚠️ Issue Type", "desc": "📝 Description",
        "submit": "Submit Request", "admin_tab": "Admin Dashboard", "user_tab": "New Ticket",
        "success": "✅ Submitted! Ticket ID: ", "error": "⚠️ Please fill all fields",
        "login": "🔐 Admin Login", "user_field": "Username", "pass_field": "Password",
        "stats_total": "Total", "stats_pending": "Pending", "stats_done": "Resolved",
        "search": "🔍 Search...", "reply_btn": "Update & Reply", "del_btn": "Delete Ticket",
        "del_all_btn": "🗑️ Delete All", "confirm_all": "Confirm Data Wipe", "dir": "ltr", "align": "left"
    }
}

# --- 3. تصميم الواجهة (CSS) وإخفاء Sidebar ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[lang]['dir']};
        text-align: {t[lang]['align']};
    }}
    /* إخفاء القائمة الجانبية تماماً */
    [data-testid="stSidebar"] {{
        display: none;
    }}
    /* تحسين التبويبات العلوية */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 20px;
        justify-content: center;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        padding: 0px 30px;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        background-color: #4361ee;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 4. القائمة العلوية (Tabs) ---
tab_user, tab_admin = st.tabs([f"🏠 {t[lang]['user_tab']}", f"📊 {t[lang]['admin_tab']}"])

# --- 5. واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1 style='text-align: center; color: #4361ee;'>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t[lang]['subtitle']}</p>", unsafe_allow_html=True)
    
    with st.form("ticket_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(t[lang]["name"])
            empid = st.text_input(t[lang]["empid"])
            email = st.text_input(t[lang]["email"])
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
with tab_admin:
    st.markdown(f"<h2 style='text-align: center;'>{t[lang]['admin_tab']}</h2>", unsafe_allow_html=True)
    
    # تسجيل الدخول في منتصف الصفحة
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.expander(t[lang]["login"], expanded=True):
            admin_user = st.text_input(t[lang]["user_field"])
            admin_pass = st.text_input(t[lang]["pass_field"], type="password")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.divider()
        # عرض الإحصائيات
        m1, m2, m3 = st.columns(3)
        m1.metric(t[lang]["stats_total"], len(df))
        m2.metric(t[lang]["stats_pending"], len(df[df['Status'].isin(["New", "جديد", "Pending", "قيد المعالجة"])]))
        m3.metric(t[lang]["stats_done"], len(df[df['Status'].isin(["Resolved", "تم الحل"])]))
        
        st.divider()
        # البحث والتصدير
        col_s, col_e = st.columns([3, 1])
        with col_s: search = st.text_input(t[lang]["search"])
        with col_e: st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)

        display_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(display_df, use_container_width=True)

        # الرد والحذف
        st.markdown("---")
        col_reply, col_del = st.columns(2)
        
        all_ids = df['ID'].tolist()
        with col_reply:
            st.subheader(t[lang]["reply_btn"])
            if all_ids:
                selected_id = st.selectbox("Ticket ID", all_ids, key="rep_id")
                reply_txt = st.text_area(t[lang]["desc"], key="rep_area")
                new_status = st.selectbox(t[lang]["type"], ["Resolved", "Pending"] if lang=="English" else ["تم الحل", "قيد المعالجة"])
                if st.button(t[lang]["reply_btn"]):
                    idx = df[df['ID'] == str(selected_id)].index[0]
                    df.at[idx, 'Reply'] = str(reply_txt)
                    df.at[idx, 'Status'] = str(new_status)
                    save_data(df)
                    st.success("Updated!")
                    st.rerun()

        with col_del:
            st.subheader(t[lang]["delete_section"])
            d_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="d_id")
            if st.button(t[lang]["del_btn"]):
                if d_id:
                    df = df[df['ID'] != str(d_id)]
                    save_data(df)
                    st.rerun()
            
            st.divider()
            confirm = st.checkbox(t[lang]["confirm_all"])
            if st.button(t[lang]["del_all_btn"]):
                if confirm:
                    df = pd.DataFrame(columns=df.columns)
                    save_data(df)
                    st.rerun()
    else:
        if admin_user: st.error("Access Denied")
