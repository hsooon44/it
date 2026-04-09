import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# محاولة استيراد مكتبة التحديث التلقائي لتجنب توقف التطبيق إذا لم تكن مثبتة
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

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
st.set_page_config(page_title="Support System", layout="wide")

if 'lang_choice' not in st.session_state:
    st.session_state.lang_choice = "العربية"

# شريط علوي لاختيار اللغة
l_col1, l_col2 = st.columns([10, 1.5])
with l_col2:
    current_lang = st.selectbox("🌐 Language", ["العربية", "English"], label_visibility="collapsed")
    if current_lang != st.session_state.lang_choice:
        st.session_state.lang_choice = current_lang
        st.rerun()

lang = st.session_state.lang_choice

# --- 3. قاموس النصوص الشامل (تم إصلاح كافة المفاتيح) ---
t = {
    "العربية": {
        "title": "نظام الدعم الفني",
        "user_tab": "طلب دعم جديد",
        "admin_tab": "لوحة الإدارة",
        "name": "👤 الاسم الكامل",
        "empid": "🆔 الرقم الوظيفي",
        "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم",
        "desc": "📝 وصف المشكلة",
        "submit": "إرسال الطلب",
        "success": "✅ تم الإرسال بنجاح!",
        "error": "⚠️ يرجى ملء الحقول المطلوبة",
        "stats_total": "إجمالي الطلبات",
        "stats_pending": "تحت المعالجة",
        "stats_done": "تم الحل",
        "search": "🔍 بحث...",
        "login": "🔐 دخول المشرف",
        "user_field": "اسم المستخدم",
        "pass_field": "كلمة المرور",
        "reply_btn": "تحديث الرد والحالة",
        "delete_section": "⚙️ إدارة البيانات",
        "del_btn": "حذف الطلب",
        "del_all_btn": "🗑️ حذف الكل",
        "confirm_all": "تأكيد المسح النهائي",
        "dir": "rtl",
        "align": "right"
    },
    "English": {
        "title": "Technical Support System",
        "user_tab": "New Ticket",
        "admin_tab": "Admin Dashboard",
        "name": "👤 Full Name",
        "empid": "🆔 Employee ID",
        "email": "📧 Email Address",
        "dept": "🏢 Department",
        "desc": "📝 Issue Description",
        "submit": "Submit Request",
        "success": "✅ Submitted successfully!",
        "error": "⚠️ Please fill required fields",
        "stats_total": "Total",
        "stats_pending": "Pending",
        "stats_done": "Resolved",
        "search": "🔍 Search...",
        "login": "🔐 Admin Login",
        "user_field": "Username",
        "pass_field": "Password",
        "reply_btn": "Update Reply & Status",
        "delete_section": "⚙️ Data Management",
        "del_btn": "Delete Ticket",
        "del_all_btn": "🗑️ Delete All",
        "confirm_all": "Confirm Deletion",
        "dir": "ltr",
        "align": "left"
    }
}

# --- 4. التنسيق (خط كبير وعريض جداً) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[lang]['dir']};
    }}

    /* تكبير الخطوط */
    h1 {{ font-size: 2.5rem !important; font-weight: 700 !important; color: #4361ee !important; text-align: center; }}
    h2 {{ font-size: 1.8rem !important; font-weight: 500 !important; text-align: center; }}
    
    label, p {{ font-size: 1.6rem !important; font-weight: 500 !important; }}
    
    input, textarea, [data-baseweb="select"] {{
        font-size: 1.4rem !important;
        font-weight: 500 !important;
    }}

    .stButton>button {{
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        height: 4rem !important;
        border-radius: 12px !important;
    }}

    [data-testid="stMetricValue"] {{ font-size: 3.5rem !important; font-weight: 900 !important; }}
    
    /* إخفاء الجانبي */
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 5. القائمة العلوية ---
tab_user, tab_admin = st.tabs([f"🏠 {t[lang]['user_tab']}", f"📊 {t[lang]['admin_tab']}"])

# --- 6. واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(t[lang]["name"])
            empid = st.text_input(t[lang]["empid"])
        with c2:
            email = st.text_input(t[lang]["email"])
            dept = st.text_input(t[lang]["dept"])
        
        issue_desc = st.text_area(t[lang]["desc"])
        
        if st.form_submit_button(t[lang]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "Status": "New" if lang=="English" else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"{t[lang]['success']} ID: {new_id}")
            else:
                st.error(t[lang]["error"])

# --- 7. واجهة الإدارة ---
with tab_admin:
    if st_autorefresh:
        st_autorefresh(interval=10000, key="auto_refresh_admin")
    
    st.markdown(f"<h2>{t[lang]['admin_tab']}</h2>", unsafe_allow_html=True)
    
    l1, l2, l3 = st.columns([1, 2, 1])
    with l2:
        with st.expander(t[lang]["login"], expanded=True):
            a_user = st.text_input(t[lang]["user_field"], key="adm_user")
            a_pass = st.text_input(t[lang]["pass_field"], type="password", key="adm_pass")

    if a_user == ADMIN_USER and a_pass == ADMIN_PASSWORD:
        st.divider()
        # إحصائيات ضخمة
        m1, m2, m3 = st.columns(3)
        m1.metric(t[lang]["stats_total"], len(df))
        m2.metric(t[lang]["stats_pending"], len(df[df['Status'].isin(["New", "جديد", "Pending", "قيد المعالجة"])]))
        m3.metric(t[lang]["stats_done"], len(df[df['Status'].isin(["Resolved", "تم الحل"])]))
        
        st.divider()
        search = st.text_input(t[lang]["search"])
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx")

        st.markdown("---")
        col_r, col_d = st.columns(2)
        all_ids = df['ID'].tolist()
        
        with col_r:
            st.subheader(t[lang]["reply_btn"])
            if all_ids:
                s_id = st.selectbox("Select ID", all_ids, key="sel_id_reply")
                r_txt = st.text_area("Reply", key="reply_area_admin")
                if st.button(t[lang]["reply_btn"], key="upd_action"):
                    idx = df[df['ID'] == s_id].index[0]
                    df.at[idx, 'Reply'] = r_txt
                    df.at[idx, 'Status'] = "Resolved" if lang=="English" else "تم الحل"
                    save_data(df)
                    st.rerun()

        with col_d:
            st.subheader(t[lang]["delete_section"])
            d_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="sel_id_del")
            if st.button(t[lang]["del_btn"], key="del_action"):
                if d_id:
                    df = df[df['ID'] != d_id]
                    save_data(df)
                    st.rerun()
            
            st.divider()
            confirm = st.checkbox(t[lang]["confirm_all"])
            if st.button(t[lang]["del_all_btn"]):
                if confirm:
                    df = pd.DataFrame(columns=df.columns)
                    save_data(df)
                    st.rerun()
