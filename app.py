import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ملفات البيانات
SALES_FILE = 'data.csv'
SUPPLIERS_FILE = 'suppliers.csv'
PRODUCTS_FILE = 'products.csv'

# تحميل المبيعات
def load_sales():
    if not os.path.exists(SALES_FILE):
        return pd.DataFrame(columns=['التاريخ', 'اسم الزبون', 'الصنف / المنتج', 'المقاس', 'المورد', 'حالة الدفع', 'تاريخ الوصول', 'حالة العميل'])
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

# تحميل الأصناف والمعدات
def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return pd.DataFrame(columns=['اسم الصنف', 'التصنيف', 'ملاحظات'])
    return pd.read_csv(PRODUCTS_FILE)

def save_products(df):
    df.to_csv(PRODUCTS_FILE, index=False)

st.set_page_config(page_title="نظام إدارة متجر الكاراتيه", layout="wide")
st.title("🥋 نظام إدارة مبيعات ومقاسات بدل ومعدات الكاراتيه")

# القائمة الجانبية المحدثة
menu = st.sidebar.selectbox("القائمة الرئيسية", ["تسجيل بيع جديد", "سجل المبيعات", "إدارة الأصناف والمنتجات", "إدارة الموردين", "متابعة الديون والمنقطعين"])

if menu == "تسجيل بيع جديد":
    st.subheader("📝 تسجيل عملية بيع جديدة")
    
    # تحميل الموردين والأصناف للقوائم المنسدلة
    suppliers_df = load_suppliers()
    supplier_list = suppliers_df['اسم المورد'].tolist() if not suppliers_df.empty else ["لا توجد موردين مضافين"]

    products_df = load_products()
    product_list = products_df['اسم الصنف'].tolist() if not products_df.empty else ["بدلة كاتا ثقيلة", "بدلة كوميتيه خفيفة"]

    with st.form("sale_form"):
        name = st.text_input("اسم الزبون")
        product_item = st.selectbox("الصنف / المنتج", product_list)
        size = st.text_input("المقاس (إن وجد)")
        supplier = st.selectbox("المورد", supplier_list)
        payment_status = st.selectbox("حالة الدفع", ["تم الدفع", "لم يدفع بعد"])
        arrival_date = st.date_input("تاريخ وصول الطلب")
        client_status = st.selectbox("حالة العميل", ["نشط", "منقطع / مؤرشف"])
        
        submit = st.form_submit_button("حفظ العملية")
        
        if submit:
            df = load_sales()
            new_data = {
                'التاريخ': datetime.now().strftime("%Y-%m-%d"), 
                'اسم الزبون': name, 
                'الصنف / المنتج': product_item, 
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

elif menu == "إدارة الأصناف والمنتجات":
    st.subheader("🏷️ دفتر الأصناف والمعدات (بدل، واقيات، ننشاكو...)")
    
    with st.form("product_form"):
        prod_name = st.text_input("اسم الصنف الجديد (مثال: واقي رأس، ننشاكو خشبي، بدلة كوميتيه)")
        prod_category = st.selectbox("التصنيف العام", ["بدلات", "واقيات وحماية", "أدوات تدريب وأسلحة", "أخرى"])
        prod_notes = st.text_input("ملاحظات إضافية")
        
        prod_submit = st.form_submit_button("حفظ الصنف الجديد")
        
        if prod_submit:
            prod_df = load_products()
            new_prod = {
                'اسم الصنف': prod_name,
                'التصنيف': prod_category,
                'ملاحظات': prod_notes
            }
            prod_df = pd.concat([prod_df, pd.DataFrame([new_prod])], ignore_index=True)
            save_products(prod_df)
            st.success("تم حفظ الصنف بنجاح! سيظهر تلقائياً في قائمة المبيعات.")
            
    st.markdown("---")
    st.subheader("قائمة الأصناف الحالية في النظام")
    prod_df = load_products()
    if not prod_df.empty:
        st.dataframe(prod_df, use_container_width=True)
    else:
        st.info("لم تقم بإضافة أصناف يدوياً بعد (يتم استخدام القائمة الافتراضية).")

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
            st.success("تم حفظ المورد بنجاح!")
            
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
            st.dataframe(unpaid[['التاريخ', 'اسم الزبون', 'الصنف / المنتج', 'المقاس', 'المورد']], use_container_width=True)
        else:
            st.success("رائع! جميع العملاء قاموا بالسداد.")
    else:
        st.info("لا توجد بيانات كافية بعد.")
