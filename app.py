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

# --- 3. نظام اختيار اللغة في الأعلى ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'AR'

lang_col1, lang_col2, lang_col3 = st.columns([4, 1, 1])
with lang_col2:
    if st.button("AR", use_container_width=True, key="btn_ar"):
        st.session_state.lang = 'AR'
        st.rerun()
with lang_col3:
    if st.button("EN", use_container_width=True, key="btn_en"):
        st.session_state.lang = 'EN'
        st.rerun()

L = st.session_state.lang

t = {
    'AR': {
        'title': "نظام الدعم الفني",
        'sub': "يرجى تعبئة النموذج أدناه وسيتم الرد عليكم قريباً",
        'name': "👤 الاسم الكامل", 'id': "🆔 الرقم الوظيفي", 'email': "📧 البريد الإلكتروني",
        'dept': "🏢 القسم", 'type': "⚠️ نوع المشكلة", 'desc': "📝 وصف المشكلة بالتفصيل",
        'submit': "إرسال الطلب", 'dir': "rtl", 'align': "right",
        'user_tab': "طلب دعم جديد", 'admin_tab': "لوحة الإدارة",
        'success': "✅ تم الإرسال بنجاح!", 'error': "⚠️ يرجى تعبئة الحقول الأساسية",
        'manage': "⚙️ إدارة الطلب المختار", 'reply': "الرد الرسمي", 'status': "تغيير الحالة",
        'del_btn': "🗑️ حذف الطلب", 'update_btn': "تحديث البيانات", 'search': "🔍 بحث في الطلبات..."
    },
    'EN': {
        'title': "IT Support System",
        'sub': "Please fill out the form below",
        'name': "👤 Full Name", 'id': "🆔 Employee ID", 'email': "📧 Email",
        'dept': "🏢 Department", 'type': "⚠️ Issue Type", 'desc': "📝 Issue Description",
        'submit': "Submit Ticket", 'dir': "ltr", 'align': "left",
        'user_tab': "New Ticket", 'admin_tab': "Admin Dashboard",
        'success': "✅ Submitted successfully!", 'error': "⚠️ Please fill all fields",
        'manage': "⚙️ Manage Selected Ticket", 'reply': "Official Reply", 'status': "Change Status",
        'del_btn': "🗑️ Delete Ticket", 'update_btn': "Update Ticket", 'search': "🔍 Search Tickets..."
    }
}

# --- 4. القائمة العلوية للتنقل (Tabs) ---
tab_user, tab_admin = st.tabs([t[L]["user_tab"], t[L]["admin_tab"]])

# --- 5. CSS لتحسين مظهر الجوال ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[L]['dir']};
    }}
    [data-testid="stForm"], .admin-container {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 10px;
    }}
    .stButton>button {{ border-radius: 10px !important; font-weight: bold !important; }}
    /* تخصيص زر الحذف */
    div[data-testid="stButton"] button:contains("حذف"), div[data-testid="stButton"] button:contains("Delete") {{
        background-color: #ff4b4b !important; color: white !important;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 6. محتوى الصفحات ---

# الصفحة الأولى: واجهة المستخدم
with tab_user:
    st.markdown(f"<h1 style='text-align: center; color: #1e3a8a;'>{t[L]['title']}</h1>", unsafe_allow_html=True)
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name, empid = st.text_input(t[L]["name"]), st.text_input(t[L]["id"])
        with c2:
            email, dept = st.text_input(t[L]["email"]), st.text_input(t[L]["dept"])
        issue_type = st.selectbox(t[L]["type"], ["Hardware", "Software", "Network", "Other"] if L == 'EN' else ["أجهزة", "أنظمة", "شبكات", "أخرى"])
        issue_desc = st.text_area(t[L]["desc"])
        if st.form_submit_button(t[L]["submit"]):
            if name and empid and issue_desc:
                new_id = str(len(df) + 1001)
                new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc, "Status": "New" if L == 'EN' else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"{t[L]['success']} ID: {new_id}")
            else: st.error(t[L]["error"])

# الصفحة الثانية: واجهة الإدارة
with tab_admin:
    st.markdown(f"<h2 style='text-align: center;'>{t[L]['admin_tab']}</h2>", unsafe_allow_html=True)
    
    l1, l2 = st.columns(2)
    admin_user = l1.text_input("User", key="au")
    admin_pass = l2.text_input("Pass", type="password", key="ap")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        st.divider()
        # شاشة عرض الطلبات
        search = st.text_input(t[L]["search"])
        filtered_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(filtered_df, use_container_width=True)
        
        st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)
        
        # خيارات التحكم والحذف
        st.markdown(f"### {t[L]['manage']}")
        all_ids = df['ID'].tolist()
        if all_ids:
            selected_id = st.selectbox("ID", all_ids)
            
            # جلب بيانات الطلب المختار للرد عليه
            row_idx = df[df['ID'] == selected_id].index[0]
            
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                new_status = st.selectbox(t[L]["status"], ["Resolved", "Pending", "In Progress"] if L == 'EN' else ["تم الحل", "قيد الانتظار", "تحت المعالجة"])
            with col_act2:
                official_reply = st.text_area(t[L]["reply"], value=df.iloc[row_idx]['Reply'])
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(t[L]["update_btn"], use_container_width=True):
                    df.at[row_idx, 'Status'] = new_status
                    df.at[row_idx, 'Reply'] = official_reply
                    save_data(df)
                    st.success("Updated!")
                    st.rerun()
            with btn_col2:
                if st.button(t[L]["del_btn"], use_container_width=True):
                    df = df[df['ID'] != selected_id]
                    save_data(df)
                    st.warning("Deleted!")
                    st.rerun()
    else:
        st.info("Please login")
