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

# --- 3. اختيار اللغة (أزرار بدلاً من قائمة) ---
# نضع اختيار اللغة في أعلى القائمة الجانبية بشكل أزرار
st.sidebar.markdown("### 🌐 Language / اللغة")
lang_choice = st.sidebar.segmented_control(
    "Select Language", 
    options=["AR", "EN"], 
    default="AR", 
    label_visibility="collapsed"
)

lang = "العربية" if lang_choice == "AR" else "English"

t = {
    "العربية": {
        "title": "طلب الدعم الفني",
        "subtitle": "يرجى تعبئة النموذج أدناه وسيتم الرد عليكم في أقرب وقت",
        "name": "👤 الاسم الكامل",
        "empid": "🆔 الرقم الوظيفي",
        "email": "📧 البريد الإلكتروني",
        "dept": "🏢 القسم",
        "type": "⚠️ نوع المشكلة",
        "desc": "📝 وصف المشكلة بالتفصيل",
        "submit": "إرسال الطلب",
        "admin_tab": "لوحة الإدارة",
        "user_tab": "طلب دعم جديد",
        "success": "✅ تم الإرسال بنجاح! رقم المتابعة: ",
        "error": "⚠️ يرجى ملء كافة الحقول",
        "login": "🔐 دخول المشرف",
        "user_field": "اسم المستخدم",
        "pass_field": "كلمة المرور",
        "stats_total": "الإجمالي",
        "stats_pending": "قيد المعالجة",
        "stats_done": "تم الحل",
        "search": "🔍 بحث...",
        "reply_btn": "تحديث الرد",
        "delete_section": "🗑️ إدارة البيانات",
        "del_btn": "حذف الطلب",
        "del_all_btn": "حذف الكل",
        "confirm_all": "تأكيد مسح البيانات",
        "dir": "rtl", "align": "right"
    },
    "English": {
        "title": "Technical Support",
        "subtitle": "Please fill out the form below",
        "name": "👤 Full Name",
        "empid": "🆔 Employee ID",
        "email": "📧 Email Address",
        "dept": "🏢 Department",
        "type": "⚠️ Issue Type",
        "desc": "📝 Issue Description",
        "submit": "Submit Request",
        "admin_tab": "Admin Dashboard",
        "user_tab": "New Ticket",
        "success": "✅ Submitted! Ticket ID: ",
        "error": "⚠️ Please fill all fields",
        "login": "🔐 Admin Login",
        "user_field": "Username",
        "pass_field": "Password",
        "stats_total": "Total",
        "stats_pending": "Pending",
        "stats_done": "Resolved",
        "search": "🔍 Search...",
        "reply_btn": "Update Reply",
        "delete_section": "🗑️ Management",
        "del_btn": "Delete Ticket",
        "del_all_btn": "Delete All",
        "confirm_all": "Confirm Data Wipe",
        "dir": "ltr", "align": "left"
    }
}

# --- 4. تحسين الواجهة للجوال (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Tajawal', sans-serif;
        direction: {t[lang]['dir']};
        text-align: {t[lang]['align']};
    }}

    /* تحسين شكل الأزرار */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #4361ee;
        color: white;
        transition: 0.3s;
    }}

    /* جعل الحقول مريحة للضغط بالإصبع */
    input, textarea, [data-baseweb="select"] {{
        border-radius: 10px !important;
    }}

    /* تصغير المسافات في الجوال */
    @media (max-width: 640px) {{
        .main .block-container {{
            padding: 1rem 0.5rem;
        }}
        h1 {{ font-size: 1.5rem !important; }}
    }}

    /* زر الحذف */
    div[data-testid="stButton"] button:contains("حذف"), 
    div[data-testid="stButton"] button:contains("Delete") {{
        background-color: #ef233c !important;
    }}
    </style>
    """, unsafe_allow_html=True)

df = load_data()

# --- 5. التنقل ---
choice = st.sidebar.radio(f"{'Menu' if lang=='English' else 'القائمة'}", [t[lang]["user_tab"], t[lang]["admin_tab"]])

# --- 6. واجهة المستخدم ---
if choice == t[lang]["user_tab"]:
    st.markdown(f"<h1 style='text-align: center; color: #4361ee;'>{t[lang]['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t[lang]['subtitle']}</p>", unsafe_allow_html=True)
    
    with st.container():
        with st.form("ticket_form", clear_on_submit=True):
            # استخدام أعمدة تترتب عمودياً تلقائياً في الجوال
            col1, col2 = st.columns([1, 1])
            with col1:
                name = st.text_input(t[lang]["name"])
                empid = st.text_input(t[lang]["empid"])
            with col2:
                email = st.text_input(t[lang]["email"])
                dept = st.text_input(t[lang]["dept"])
            
            issue_type = st.selectbox(t[lang]["type"], ["Hardware", "Software", "Network", "Other"] if lang=="English" else ["أجهزة", "أنظمة", "شبكات", "أخرى"])
            issue_desc = st.text_area(t[lang]["desc"], height=150)
            
            submit = st.form_submit_button(t[lang]["submit"])
            
            if submit:
                if name and empid and dept and issue_desc:
                    new_id = str(len(df) + 1001)
                    new_row = {"ID": new_id, "Name": name, "EmpID": empid, "Email": email, "Department": dept, "IssueType": issue_type, "IssueDesc": issue_desc, "Status": "New" if lang=="English" else "جديد", "Reply": "No reply", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success(f"{t[lang]['success']} {new_id}")
                else:
                    st.error(t[lang]["error"])

# --- 7. واجهة الإدارة ---
else:
    st.markdown(f"<h1 style='text-align: center;'>{t[lang]['admin_tab']}</h1>", unsafe_allow_html=True)
    with st.sidebar.expander(t[lang]["login"]):
        admin_user = st.text_input(t[lang]["user_field"])
        admin_pass = st.text_input(t[lang]["pass_field"], type="password")

    if admin_user == ADMIN_USER and admin_pass == ADMIN_PASSWORD:
        # إحصائيات سريعة (تظهر بشكل عرضي)
        c1, c2, c3 = st.columns(3)
        c1.metric(t[lang]["stats_total"], len(df))
        c2.metric(t[lang]["stats_pending"], len(df[df['Status'].isin(["New", "جديد", "Pending", "قيد المعالجة"])]))
        c3.metric(t[lang]["stats_done"], len(df[df['Status'].isin(["Resolved", "تم الحل"])]))
        
        st.divider()
        
        # البحث والتصدير
        col_search, col_export = st.columns([2, 1])
        with col_search: search = st.text_input(t[lang]["search"])
        with col_export: 
            st.write(" ")
            st.download_button("📥 Excel", data=to_excel(df), file_name="tickets.xlsx", use_container_width=True)

        display_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)] if search else df
        st.dataframe(display_df, use_container_width=True)

        # الإجراءات
        st.markdown("---")
        tab1, tab2 = st.tabs([t[lang]["reply_btn"], t[lang]["delete_section"]])
        
        with tab1:
            all_ids = df['ID'].tolist()
            if all_ids:
                selected_id = st.selectbox("ID", all_ids)
                reply_text = st.text_area(f"Reply")
                status_options = ["Resolved", "Pending"] if lang == "English" else ["تم الحل", "قيد المعالجة"]
                new_status = st.selectbox(t[lang]["type"], status_options)
                if st.button(t[lang]["reply_btn"], key="update"):
                    idx = df[df['ID'] == str(selected_id)].index[0]
                    df.iloc[idx, df.columns.get_loc('Reply')] = str(reply_text)
                    df.iloc[idx, df.columns.get_loc('Status')] = str(new_status)
                    save_data(df)
                    st.rerun()

        with tab2:
            del_id = st.selectbox(t[lang]["del_btn"], [None] + all_ids)
            if st.button(t[lang]["del_btn"]):
                if del_id:
                    df = df[df['ID'] != str(del_id)]
                    save_data(df)
                    st.rerun()
            
            st.divider()
            confirm_del = st.checkbox(t[lang]["confirm_all"])
            if st.button(t[lang]["del_all_btn"]):
                if confirm_del:
                    df = pd.DataFrame(columns=df.columns)
                    save_data(df)
                    st.rerun()
    else:
        st.warning("Admin access required")
