import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ملفات البيانات
SALES_FILE = 'data.csv'
SUPPLIERS_FILE = 'suppliers.csv'

# تحميل المبيعات
def load_sales():
    if not os.path.exists(SALES_FILE):
        return pd.DataFrame(columns=['التاريخ', 'اسم الزبون', 'نوع البدلة', 'المقاس', 'المورد', 'حالة الدفع', 'تاريخ الوصول', 'حالة العميل'])
    return pd.read_csv(SALES_FILE)

def save_sales(df):
    df.to_csv(SALES_FILE, index=False)

# تحميل الموردين
def load_suppliers():
    if not os.path.exists(SUPPLIERS_FILE):
        return pd.DataFrame(columns=['اسم المورد', 'رقم الجوال', 'الموقع', 'البراندات', 'الحالة'])
    return pd.read_csv(SUPPLIERS_FILE)

def save_suppliers(df):
    df.to_csv(SUPPLIERS_FILE, index=False)

st.set_page_config(page_title="نظام إدارة بدل الكاراتيه", layout="wide")
st.title("🥋 نظام إدارة مبيعات ومقاسات بدل الكاراتيه والموردين")

# القائمة الجانبية
menu = st.sidebar.selectbox("القائمة الرئيسية", ["تسجيل بيع جديد", "سجل المبيعات", "إدارة الموردين", "متابعة الديون والمنقطعين"])

if menu == "تسجيل بيع جديد":
    st.subheader("📝 تسجيل عملية بيع جديدة")
    
    suppliers_df = load_suppliers()
    supplier_list = suppliers_df['اسم المورد'].tolist() if not suppliers_df.empty else ["لا توجد موردين مضافين"]

    with st.form("sale_form"):
        name = st.text_input("اسم الزبون")
        suit_type = st.selectbox("نوع البدلة", ["بدلة كاتا ثقيلة", "بدلة كوميتيه خفيفة", "بدلة تدريب عادية"])
        size = st.text_input("المقاس")
        supplier = st.selectbox("المورد", supplier_list)
        payment_status = st.selectbox("حالة الدفع", ["تم الدفع", "لم يدفع بعد"])
        arrival_date = st.date_input("تاريخ وصول البدلة")
        client_status = st.selectbox("حالة العميل", ["نشط", "منقطع / مؤرشف"])
        
        submit = st.form_submit_button("حفظ العملية")
        
        if submit:
            df = load_sales()
            new_data = {
                'التاريخ': datetime.now().strftime("%Y-%m-%d"), 
                'اسم الزبون': name, 
                'نوع البدلة': suit_type, 
                'المقاس': size, 
                'المورد': supplier, 
                'حالة الدفع': payment_status, 
                'تاريخ الوصول': arrival_date,
                'حالة العميل': client_status
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_sales(df)
            st.success("تم حفظ العملية بنجاح!")

elif menu == "سجل المبيعات":
    st.subheader("📊 سجل المبيعات الكامل")
    df = load_sales()
    if not df.empty:
        filter_status = st.radio("عرض حسب حالة العميل:", ["النشطين فقط", "المنقطعين فقط", "الكل"], horizontal=True)
        if filter_status == "النشطين فقط":
            df = df[df['حالة العميل'] == "نشط"]
        elif filter_status == "المنقطعين فقط":
            df = df[df['حالة العميل'] == "منقطع / مؤرشف"]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد مبيعات مسجلة حتى الآن.")

elif menu == "إدارة الموردين":
    st.subheader("🤝 دفتر الموردين والبراندات")
    
    with st.form("supplier_form"):
        sup_name = st.text_input("اسم المورد / الشركة")
        sup_phone = st.text_input("رقم الجوال")
        sup_location = st.text_input("الموقع (المدينة / الحي)")
        sup_brands = st.text_input("البراندات التي يوردها")
        sup_status = st.selectbox("حالة التعامل مع المورد", ["نشط", "منقطع التعامل"])
        
        sup_submit = st.form_submit_button("حفظ المورد")
        
        if sup_submit:
            sup_df = load_suppliers()
            new_sup = {
                'اسم المورد': sup_name,
                'رقم الجوال': sup_phone,
                'الموقع': sup_location,
                'البراندات': sup_brands,
                'الحالة': sup_status
            }
            sup_df = pd.concat([sup_df, pd.DataFrame([new_sup])], ignore_index=True)
            save_suppliers(sup_df)
            st.success("تم حفظ المورد بنجاح! (قم بتحديث الصفحة لتظهر القائمة)")
            
    st.markdown("---")
    st.subheader("قائمة الموردين الحاليين")
    sup_df = load_suppliers()
    if not sup_df.empty:
        st.dataframe(sup_df, use_container_width=True)
    else:
        st.info("لم يتم إضافة أي موردين بعد.")

elif menu == "متابعة الديون والمنقطعين":
    st.subheader("🗄️ متابعة الديون والعملاء")
    df = load_sales()
    if not df.empty:
        unpaid = df[df['حالة الدفع'] == "لم يدفع بعد"]
        st.markdown("### ⚠️ عملاء لم يدفعوا حتى الآن (ديون معلقة):")
        if not unpaid.empty:
            st.dataframe(unpaid[['التاريخ', 'اسم الزبون', 'نوع البدلة', 'المقاس', 'المورد']], use_container_width=True)
        else:
            st.success("رائع! جميع العملاء قاموا بالسداد.")
    else:
        st.info("لا توجد بيانات كافية بعد.")
