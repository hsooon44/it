import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# ==========================================
# إعداد المهندس / حسن زحيفي
# نظام الدعم الفني - جميع الحقوق محفوظة
# ==========================================

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

def get_time_status(date_str, status):
    if status in ["تم الحل", "Resolved"]:
        return "🟢 Resolved ✅"
    try:
        start_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        duration = datetime.now() - start_time
        total_minutes = int(duration.total_seconds() / 60)
        if total_minutes <= 60:
            return f"🟢 {total_minutes} min"
        elif 60 < total_minutes <= 180:
            hours = total_minutes // 60
            mins = total_minutes % 60
            return f"🟡 {hours}h {mins}m"
        else:
            hours = total_minutes // 60
            return f"🔴 {hours}h+"
    except:
        return "⚪ N/A"

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Support System", layout="wide")

if 'lang_choice' not in st.session_state:
    st.session_state.lang_choice = "العربية"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
# عداد لتصفير الحقول
if 'form_iteration' not in st.session_state:
    st.session_state.form_iteration = 0

lang = st.session_state.lang_choice

t = {
    "العربية": {
        "title": "نظام الدعم الفني", "user_tab": "طلب دعم جديد", "admin_tab": "لوحة الإدارة",
        "name": "👤 الاسم الكامل", "empid": "🆔 الرقم الوظيفي", "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم", "desc": "📝 وصف المشكلة", "submit": "إرسال الطلب",
        "status_options": ["جديد", "قيد المعالجة", "تم الحل", "لم يتم الحل"],
        "login_btn": "دخول", "search": "🔍 بحث...", "dir": "rtl",
        "user_label": "اسم المستخدم", "pass_label": "كلمة المرور",
        "manage_title": "⚙️ معالجة الطلب", "update_btn": "تحديث البيانات ✅",
        "reply_label": "الرد الرسمي", "stat_label": "تحديث الحالة",
        "del_section": "🗑️ إدارة الحذف", "del_btn": "🗑️ حذف الطلب", 
        "del_all": "🗑️ حذف كافة البيانات", "confirm": "تأكيد الحذف النهائي",
        "stats_total": "إجمالي الطلبات", "stats_new": "طلبات جديدة", 
        "stats_proc": "قيد المعالجة", "stats_done": "تم الحل",
        "success_msg": "تم التحديث بنجاح", "error_confirm": "يرجى التأكيد أولاً",
        "time_col": "⏱️ مدة الطلب",
        "copyright": "إعداد المهندس / حسن زحيفي"
    },
    "English": {
        "title": "Technical Support System", "user_tab": "New Ticket", "admin_tab": "Admin Dashboard",
        "name": "👤 Full Name", "empid": "🆔 Employee ID", "email": "📧 Email",
        "dept": "🏢 Department", "desc": "📝 Issue Description", "submit": "Submit Ticket",
        "status_options": ["New", "In Progress", "Resolved", "Not Resolved"],
        "login_btn": "Login", "search": "🔍 Search...", "dir": "ltr",
        "user_label": "Username", "pass_label": "Password",
        "manage_title": "⚙️ Ticket Processing", "update_btn": "Update Data ✅",
        "reply_label": "Official Reply", "stat_label": "Update Status",
        "del_section": "🗑️ Delete Management", "del_btn": "🗑️ Delete Ticket", 
        "del_all": "🗑️ Wipe All Data", "confirm": "Confirm Final Deletion",
        "stats_total": "Total Tickets", "stats_new": "New", 
        "stats_proc": "In Progress", "stats_done": "Resolved",
        "success_msg": "Updated Successfully", "error_confirm": "Please confirm first",
        "time_col": "⏱️ Ticket Duration",
        "copyright": "Prepared by Engr. Hassan Zuhayfi"
    }
}

# --- 3. التنسيق (تعريض كافة الخطوط) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@700;900&display=swap');
    
    * {{
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 800 !important; /* تعريض عام لجميع النصوص */
    }}
    
    html, body, [data-testid="stAppViewContainer"] {{ 
        direction: {t[lang]['dir']}; 
    }}

    h1 {{ font-size: 3.2rem !important; font-weight: 900 !important; color: #4361ee !important; text-align: center; }}
    h3, .stSubheader {{ font-size: 1.8rem !important; font-weight: 900 !important; }}
    
    /* تعريض خطوط الجداول */
    [data-testid="stTable"], [data-testid="stDataFrame"] {{ font-weight: 800 !important; }}
    
    /* تعريض خطوط الأزرار */
    .stButton>button {{ 
        font-size: 1.2rem !important; 
        font-weight: 900 !important; 
        border-radius: 10px !important; 
    }}

    /* تعريض خطوط حقول الإدخال */
    input, textarea, [data-baseweb="select"] {{
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }}

    [data-testid="stSidebar"] {{ display: none; }}
    
    .footer {{ 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background-color: rgba(255,255,255,0.8); 
        color: #333; text-align: center; font-size: 16px; 
        padding: 10px; font-weight: 900 !important;
        border-top: 1px solid #ddd;
    }}
    </style>
    """, unsafe_allow_html=True)

# أزرار اللغة
col_spacer, col_en, col_ar = st.columns([10, 0.8, 0.8])
with col_en:
    if st.button("EN", use_container_width=True):
        st.session_state.lang_choice = "English"; st.rerun()
with col_ar:
    if st.button("AR", use_container_width=True):
        st.session_state.lang_choice = "العربية"; st.rerun()

df = load_data()
tab_user, tab_admin = st.tabs([f"🏠 {t[lang]['user_tab']}", f"📊 {t[lang]['admin_tab']}"])

# --- واجهة المستخدم ---
with tab_user:
    st.markdown(f"<h1>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input(t[lang]["name"])
        empid = c1.text_input(t[lang]["empid"])
        email = c2.text_input(t[lang]["email"])
        dept = c2.text_input(t[lang]["dept"])
        issue_desc = st.text_area(t[lang]["desc"], height=150) 
        if st.form_submit_button(t[lang]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueDesc": issue_desc, "Status": t[lang]["status_options"][0], "Reply": "---", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df); st.success(f"Ticket ID: {new_id}")

# --- واجهة الإدارة ---
with tab_admin:
    if st_autorefresh:
        st_autorefresh(interval=10000, key="admin_ref")

    if not st.session_state.logged_in:
        st.markdown(f"### {t[lang]['login_btn']}")
        l_col1, l_col2, l_col3 = st.columns([1.5, 1.5, 0.6])
        a_user = l_col1.text_input(t[lang]["user_label"], key="u_field")
        a_pass = l_col2.text_input(t[lang]["pass_label"], type="password", key="p_field")
        if l_col3.button(t[lang]["login_btn"], use_container_width=True):
            if a_user == ADMIN_USER and a_pass == ADMIN_PASSWORD:
                st.session_state.logged_in = True; st.rerun()

    if st.session_state.logged_in:
        st.markdown(f"### {t[lang]['admin_tab']}")
        stats = {"total": len(df), "new": len(df[df['Status'].isin(["جديد", "New"])]), "proc": len(df[df['Status'].isin(["قيد المعالجة", "In Progress"])]), "done": len(df[df['Status'].isin(["تم الحل", "Resolved"])])}
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(t[lang]["stats_total"], stats["total"]); m2.metric(t[lang]["stats_new"], stats["new"]); m3.metric(t[lang]["stats_proc"], stats["proc"]); m4.metric(t[lang]["stats_done"], stats["done"])
        st.divider()
        
        c_search, c_excel = st.columns([4, 1])
        search = c_search.text_input(t[lang]["search"])
        c_excel.write("##")
        c_excel.download_button("📤 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)
        
        df_display = df.copy()
        if not df_display.empty:
            df_display[t[lang]["time_col"]] = df_display.apply(lambda x: get_time_status(x['Date'], x['Status']), axis=1)
            if search:
                df_display = df_display[df_display.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
            cols = [t[lang]["time_col"]] + [c for c in df_display.columns if c != t[lang]["time_col"]]
            st.dataframe(df_display[cols], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        all_ids = df['ID'].tolist()
        if all_ids:
            col_manage, col_delete = st.columns([2, 1])
            with col_manage:
                st.subheader(t[lang]["manage_title"])
                sel_id = st.selectbox("ID", all_ids, key="sel_process")
                idx = df[df['ID'] == sel_id].index[0]
                st.info(f"**{t[lang]['desc']}:** {df.at[idx, 'IssueDesc']}")
                
                cs1, cs2 = st.columns(2)
                
                # تحديث المفاتيح لضمان التصفير التام
                new_stat = cs1.selectbox(t[lang]["stat_label"], t[lang]["status_options"], key=f"stat_key_{st.session_state.form_iteration}")
                
                # استخدام قيمة فارغة ابتدائية عند التحديث
                new_rep = cs2.text_area(t[lang]["reply_label"], key=f"rep_key_{st.session_state.form_iteration}", height=100)
                
                if st.button(t[lang]["update_btn"], use_container_width=True):
                    df.at[idx, 'Status'] = new_stat
                    df.at[idx, 'Reply'] = new_rep
                    save_data(df)
                    st.session_state.form_iteration += 1 # تغيير الـ keys لتصفير الحقول
                    st.success(t[lang]["success_msg"])
                    st.rerun()

            with col_delete:
                st.subheader(t[lang]["del_section"])
                d_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids, key="d_sel_one")
                if st.button(t[lang]["del_btn"], use_container_width=True):
                    if d_id:
                        df = df[df['ID'] != d_id]; save_data(df); st.rerun()
                st.divider()
                confirm = st.checkbox(t[lang]["confirm"], key="conf_del_all")
                if st.button(t[lang]["del_all"], use_container_width=True):
                    if confirm:
                        df = pd.DataFrame(columns=df.columns); save_data(df); st.rerun()
                    else: st.error(t[lang]["error_confirm"])

# --- حقوق المهندس حسن زحيفي ---
st.markdown(f'<div class="footer">{t[lang]["copyright"]}</div>', unsafe_allow_html=True)
