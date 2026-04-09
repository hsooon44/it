import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# محاولة استيراد مكتبة التحديث التلقائي
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
    return pd.DataFrame(columns=["ID", "Name", "EmpID", "Email", "Department", "IssueDesc", "Status", "Reply", "Date"])

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
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# أزرار تبديل اللغة العلوية
col_spacer, col_en, col_ar = st.columns([10, 0.8, 0.8])
with col_en:
    if st.button("EN", use_container_width=True):
        st.session_state.lang_choice = "English"; st.rerun()
with col_ar:
    if st.button("AR", use_container_width=True):
        st.session_state.lang_choice = "العربية"; st.rerun()

lang = st.session_state.lang_choice

t = {
    "العربية": {
        "title": "نظام الدعم الفني", "user_tab": "طلب دعم جديد", "admin_tab": "لوحة الإدارة",
        "name": "👤 الاسم الكامل", "empid": "🆔 الرقم الوظيفي", "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم", "desc": "📝 وصف المشكلة", "submit": "إرسال الطلب",
        "status_options": ["جديد", "قيد المعالجة", "تم الحل", "لم يتم الحل"],
        "login_btn": "دخول", "search": "🔍 بحث...", "dir": "rtl",
        "del_btn": "🗑️ حذف الطلب", "del_all": "🗑️ حذف الكل", "confirm": "تأكيد"
    },
    "English": {
        "title": "Support System", "user_tab": "New Ticket", "admin_tab": "Dashboard",
        "name": "👤 Full Name", "empid": "🆔 Employee ID", "email": "📧 Email",
        "dept": "🏢 Department", "desc": "📝 Description", "submit": "Submit",
        "status_options": ["New", "In Progress", "Resolved", "Not Resolved"],
        "login_btn": "Login", "search": "🔍 Search...", "dir": "ltr",
        "del_btn": "🗑️ Delete", "del_all": "🗑️ Wipe Data", "confirm": "Confirm"
    }
}

# --- 3. التنسيق (CSS) الحل الجذري لإخفاء المستطيل ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Tajawal', sans-serif; direction: {t[lang]['dir']}; }}
    h1 {{ font-size: 3rem !important; font-weight: 900 !important; color: #4361ee !important; text-align: center; }}
    label, p {{ font-size: 1.4rem !important; font-weight: 700 !important; }}
    .stButton>button {{ font-size: 1.3rem !important; font-weight: 800 !important; border-radius: 10px !important; }}
    
    /* 1. منع تغيير الحجم لجميع مربعات النص */
    textarea {{ 
        resize: none !important; 
    }}
    
    /* 2. استهداف الطبقات العميقة لإخفاء رمز التكبير تماماً */
    [data-testid="stTextArea"] textarea {{
        resize: none !important;
    }}
    
    /* 3. إخفاء مقبض التغيير في متصفحات Chrome/Safari */
    [data-testid="stTextArea"] textarea::-webkit-resizer {{
        display: none !important;
        -webkit-appearance: none !important;
    }}

    /* 4. إخفاء الحاوية التي قد تحمل مقبض التغيير */
    .stTextArea div[data-baseweb="textarea"] {{
        resize: none !important;
    }}

    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 4. التبويبات ---
tab_user, tab_admin = st.tabs([f"🏠 {t[lang]['user_tab']}", f"📊 {t[lang]['admin_tab']}"])

# --- 5. واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input(t[lang]["name"])
        empid = c1.text_input(t[lang]["empid"])
        email = c2.text_input(t[lang]["email"])
        dept = c2.text_input(t[lang]["dept"])
        
        # حقل وصف المشكلة
        issue_desc = st.text_area(t[lang]["desc"], height=150) 
        
        if st.form_submit_button(t[lang]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueDesc": issue_desc, "Status": t[lang]["status_options"][0], "Reply": "---", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df); st.success(f"ID: {new_id}")

# --- 6. واجهة الإدارة ---
with tab_admin:
    if st_autorefresh:
        st_autorefresh(interval=10000, key="admin_ref")

    if not st.session_state.logged_in:
        st.markdown(f"### {t[lang]['admin_tab']}")
        l_col1, l_col2, l_col3 = st.columns([1.5, 1.5, 0.6])
        a_user = l_col1.text_input("User", key="u_field")
        a_pass = l_col2.text_input("Password", type="password", key="p_field")
        st.write("##")
        if l_col3.button(t[lang]["login_btn"], use_container_width=True):
            if a_user == ADMIN_USER and a_pass == ADMIN_PASSWORD:
                st.session_state.logged_in = True; st.rerun()

    if st.session_state.logged_in:
        c_search, c_excel = st.columns([4, 1])
        search = c_search.text_input(t[lang]["search"])
        c_excel.write("##")
        c_excel.download_button("📤 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)
        
        display_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(display_df, use_container_width=True)

        st.markdown("---")
        all_ids = df['ID'].tolist()
        if all_ids:
            col_manage, col_delete = st.columns([2, 1])
            with col_manage:
                st.subheader("⚙️ معالجة الطلب")
                sel_id = st.selectbox("ID", all_ids, key="sel_process")
                idx = df[df['ID'] == sel_id].index[0]
                st.info(f"**وصف المشكلة:** {df.at[idx, 'IssueDesc']}")
                cs1, cs2 = st.columns(2)
                new_stat = cs1.selectbox("الحالة", t[lang]["status_options"], key="stat_update")
                new_rep = cs2.text_area("الرد الرسمي", value=df.at[idx, 'Reply'], key="rep_update", height=100)
                if st.button("تحديث ✅", use_container_width=True):
                    df.at[idx, 'Status'] = new_stat
                    df.at[idx, 'Reply'] = new_rep
                    save_data(df); st.success("تم التحديث"); st.rerun()

            with col_delete:
                st.subheader("🗑️")
                d_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="d_sel_one")
                if st.button(t[lang]["del_btn"], use_container_width=True):
                    if d_id:
                        df = df[df['ID'] != d_id]
                        save_data(df); st.rerun()
                st.divider()
                confirm = st.checkbox(t[lang]["confirm"], key="conf_del_all")
                if st.button(t[lang]["del_all"], use_container_width=True):
                    if confirm:
                        df = pd.DataFrame(columns=df.columns)
                        save_data(df); st.rerun()
