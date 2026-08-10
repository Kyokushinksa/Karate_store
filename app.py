import streamlit as st
import pandas as pd
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نظام الكاراتيه", page_icon="🥋", layout="wide")

# --- 2. تطبيق تأثير الخلفية المائية (الكانجي بلون رصاصي خفيف في كل الشاشات) ---
background_css = """
<style>
/* خلفية مائية لشعار الكانجي في جميع الشاشات */
.stApp {
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/1/12/Kyokushin_kanji.svg");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 40% auto;
    background-attachment: fixed;
}
/* إضافة طبقة شفافة خفيفة جداً لضمان قراءة النصوص فوق الخلفية بوضوح */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(14, 17, 23, 0.92); /* خلفية داكنة متناسقة مع الشفافية */
    z-index: -1;
}
</style>
"""
st.markdown(background_css, unsafe_allow_html=True)

# --- 3. المتغيرات الأساسية ---
SECRET_PIN = "1234"  # الرقم السري للدخول

# --- 4. إنشاء ملفات البيانات محلياً (مع قراءة المقاسات كنصوص حصرياً) ---
def init_files():
    if not os.path.exists("sales.csv"):
        pd.DataFrame(columns=["التاريخ", "اسم العميل", "رقم الجوال", "المنتج", "المقاس", "السعر"]).to_csv("sales.csv", index=False)
    if not os.path.exists("suppliers.csv"):
        pd.DataFrame(columns=["اسم المورد", "رقم الجوال", "ملاحظات"]).to_csv("suppliers.csv", index=False)
    if not os.path.exists("sizes.csv"):
        pd.DataFrame({"المقاس": ["000", "00", "0", "1", "2", "3", "4", "5", "6", "7"]}).to_csv("sizes.csv", index=False)

init_files()

# --- 5. شاشة الحماية (تسجيل الدخول) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🥋 نظام إدارة متجر الكيوكوشن</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>الرجاء إدخال الرقم السري</h3>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        pin_input = st.text_input("الرقم السري:", type="password")
        submit_btn = st.form_submit_button("دخول")
        
        if submit_btn:
            if pin_input == SECRET_PIN:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ الرقم السري غير صحيح!")
    st.stop()

# ==========================================
# --- التطبيق الرئيسي ---
# ==========================================

# --- الشريط الجانبي (Sidebar) ---
st.sidebar.markdown("<h1 style='text-align: center;'>🥋 极真会</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #ff4b4b;'>KYOKUSHIN</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.header("القائمة الرئيسية")

menu = st.sidebar.radio("اختر الصفحة:", ["المبيعات 🛒", "الموردين 🤝", "دفتر المقاسات 📏"])

st.sidebar.markdown("---")
if st.sidebar.button("تسجيل الخروج 🔒"):
    st.session_state.authenticated = False
    st.rerun()

# --- قراءة المقاسات كنصوص (dtype=str) لحماية الأصفار 000 و 00 ---
df_sizes = pd.read_csv("sizes.csv", dtype=str)

# ==========================================
# 1. صفحة المبيعات
# ==========================================
if menu == "المبيعات 🛒":
    st.title("🛒 إدارة المبيعات")
    
    with st.form("add_sale_form", clear_on_submit=True):
        st.subheader("إضافة مبيعة جديدة")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("التاريخ")
            customer_name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الجوال")
        with col2:
            item = st.text_input("المنتج (مثال: بدلة، واقيات)")
            size = st.selectbox("المقاس", df_sizes["المقاس"].tolist())
            price = st.number_input("السعر", min_value=0.0, step=10.0)
            
        save_sale = st.form_submit_button("حفظ المبيعة 💾")
        
        if save_sale:
            new_sale = pd.DataFrame({"التاريخ": [date], "اسم العميل": [customer_name], "رقم الجوال": [phone], "المنتج": [item], "المقاس": [str(size)], "السعر": [price]})
            new_sale.to_csv("sales.csv", mode='a', header=False, index=False)
            st.success("✅ تم الحفظ وتفريغ الخانات تلقائياً!")
            st.rerun()

    st.markdown("---")
    st.subheader("📊 سجل المبيعات")
    st.dataframe(pd.read_csv("sales.csv", dtype=str), use_container_width=True)

# ==========================================
# 2. صفحة الموردين 
# ==========================================
elif menu == "الموردين 🤝":
    st.title("🤝 إدارة الموردين")
    
    with st.form("add_supplier_form", clear_on_submit=True):
        st.subheader("إضافة مورد جديد")
        supp_name = st.text_input("اسم المورد")
        supp_phone = st.text_input("رقم الجوال")
        supp_notes = st.text_area("تفاصيل / ملاحظات")
        
        save_supplier = st.form_submit_button("حفظ المورد 💾")
        
        if save_supplier:
            if supp_name:
                new_supp = pd.DataFrame({"اسم المورد": [supp_name], "رقم الجوال": [supp_phone], "ملاحظات": [supp_notes]})
                new_supp.to_csv("suppliers.csv", mode='a', header=False, index=False)
                st.success("✅ تم حفظ المورد بنجاح!")
                st.rerun()
            else:
                st.error("❌ يجب كتابة اسم المورد على الأقل.")
                
    st.markdown("---")
    st.subheader("📋 قائمة الموردين")
    st.dataframe(pd.read_csv("suppliers.csv", dtype=str), use_container_width=True)

# ==========================================
# 3. صفحة إدارة المقاسات
# ==========================================
elif menu == "دفتر المقاسات 📏":
    st.title("📏 دفتر المقاسات")
    st.info("💡 أي مقاس تضيفه هنا، سيظهر تلقائياً في قائمة المقاسات عند تسجيل المبيعات.")
    
    with st.form("add_size_form", clear_on_submit=True):
        st.subheader("إضافة مقاس جديد")
        new_size = st.text_input("اسم/رقم المقاس (مثال: XXL, 8, خاص)")
        save_size = st.form_submit_button("إضافة المقاس ➕")
        
        if save_size:
            if new_size and new_size not in df_sizes["المقاس"].tolist():
                new_size_df = pd.DataFrame({"المقاس": [str(new_size)]})
                new_size_df.to_csv("sizes.csv", mode='a', header=False, index=False)
                st.success(f"✅ تم إضافة المقاس ({new_size}) بنجاح!")
                st.rerun()
            else:
                st.warning("⚠️ هذا المقاس موجود مسبقاً أو الحقل فارغ!")
                
    st.markdown("---")
    st.subheader("📋 المقاسات المتوفرة")
    st.dataframe(df_sizes, use_container_width=True)
