import pandas as pd
import streamlit as st
import os
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة مبيعات بدل الكاراتيه", page_icon="🥋", layout="wide"
)

# اسم ملف حفظ البيانات
DATA_FILE = "karate_sales_data.csv"


# تحميل أو إنشاء قاعدة البيانات
def load_data():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  else:
    # إنشاء جدول فارغ بالأعمدة المطلوبة
    df = pd.DataFrame(columns=[
        "رقم الفاتورة",
        "التاريخ",
        "اسم الزبون / المتدرب",
        "نوع البدلة",
        "المقاس",
        "السعر الإجمالي (ريال)",
        "المبلغ المدفوع (ريال)",
        "المتبقي (ريال)",
        "حالة الدفع",
    ])
    return df


df = load_data()

# عنوان التطبيق
st.title("🥋 نظام إدارة مبيعات ومقاسات بدل الكاراتيه")
st.markdown("---")

# القائمة الجانبية للتنقل بين الصفحات
menu = st.sidebar.selectbox(
    "اختر القناة:",
    ["تسجيل بيع جديد", "سجل المبيعات والحسابات", "إدارة المخزون والمقاسات"],
)

# ---------------------------------------------------------
# 1. صفحة تسجيل بيع جديد
# ---------------------------------------------------------
if menu == "تسجيل بيع جديد":
  st.header("📝 تسجيل عملية بيع جديدة")

  with st.form("sale_form"):
    col1, col2 = st.columns(2)

    with col1:
      customer_name = st.text_input("اسم الزبون / المتدرب")
      suit_type = st.selectbox(
          "نوع البدلة",
          [
              "بدلة كاتا ثقيلة (Kata)",
              "بدلة كوميتي خفيفة (Kumite)",
              "بدلة تدريب عادي",
          ],
      )
      size = st.selectbox(
          "المقاس",
          [
              "مقاس 000 / 110 سم",
              "مقاس 00 / 120 سم",
              "مقاس 0 / 130 سم",
              "مقاس 1 / 140 سم",
              "مقاس 2 / 150 سم",
              "مقاس 3 / 160 سم",
              "مقاس 4 / 170 سم",
              "مقاس 5 / 180 سم",
              "مقاس 6 / 190 سم",
          ],
      )

    with col2:
      total_price = st.number_input(
          "السعر الإجمالي (ريال)", min_value=0.0, step=10.0
      )
      paid_amount = st.number_input(
          "المبلغ المدفوع (ريال)", min_value=0.0, step=10.0
      )

    submitted = st.form_submit_button("حفظ العملية")

    if submitted:
      if not customer_name:
        st.warning("⚠️ يرجى إدخال اسم الزبون أو المتدرب.")
      else:
        # حساب المتبقي
        remaining = total_price - paid_amount
        payment_status = "خالص" if remaining <= 0 else "متبقي مبلغ"

        # توليد رقم فاتورة فريد يعتمد على التاريخ والوقت
        invoice_id = datetime.now().strftime("%Y%m%d%H%M%S")
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # إضافة البيانات للجدول
        new_row = {
            "رقم الفاتورة": invoice_id,
            "التاريخ": current_date,
            "اسم الزبون / المتدرب": customer_name,
            "نوع البدلة": suit_type,
            "المقاس": size,
            "السعر الإجمالي (ريال)": total_price,
            "المبلغ المدفوع (ريال)": paid_amount,
            "المتبقي (ريال)": remaining,
            "حالة الدفع": payment_status,
        }

        # استخدام pandas لإضافة السطر وحفظه
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success(
            f"✅ تم تسجيل العملية بنجاح! المبلغ المتبقي على الزبون: **{remaining}"
            " ريال**"
        )

# ---------------------------------------------------------
# 2. صفحة سجل المبيعات والحسابات
# ---------------------------------------------------------
elif menu == "سجل المبيعات والحسابات":
  st.header("📊 سجل المبيعات والديون والمتبقيات")

  if df.empty:
    st.info("لا توجد مبيعات مسجلة حتى الآن.")
  else:
    # إحصائيات سريعة
    total_sales = df["السعر الإجمالي (ريال)"].sum()
    total_collected = df["المبلغ المدفوع (ريال)"].sum()
    total_remaining = df["المتبقي (ريال)"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المبيعات", f"{total_sales} ريال")
    col2.metric("المبالغ المحصلة", f"{total_collected} ريال")
    col3.metric("إجمالي الديون (المتبقي)", f"{total_remaining} ريال")

    st.markdown("---")

    # خيار البحث عن زبون
    search_query = st.text_input(
        "🔍 بحث بالاسم أو رقم الفاتورة:", ""
    )
    if search_query:
      filtered_df = df[
          df["اسم الزبون / المتدرب"]
              .str.contains(search_query, na=False)
          | df["رقم الفاتورة"].astype(str).str.contains(search_query, na=False)
      ]
    else:
      filtered_df = df

    # عرض الجدول
    st.dataframe(filtered_df, use_container_width=True)

    # زر لتصدير البيانات أو مسح السجلات إذا لزم الأمر
    if st.button("حذف كافة السجلات (إعادة ضبط)"):
      if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("تم مسح السجلات بنجاح. أعد تحميل الصفحة.")
        st.rerun()

# ---------------------------------------------------------
# 3. صفحة إدارة المخزون والمقاسات
# ---------------------------------------------------------
elif menu == "إدارة المخزون والمقاسات":
  st.header("📦 نظرة عامة على مقاسات البدل المتاحة")
  st.write(
      "هنا يمكنك اعتماد دليل المقاسات الخاص بك ليكون مرجعاً أثناء عملية البيع:"
  )

  sizes_guide = {
      "المقاس": [
          "مقاس 000",
          "مقاس 00",
          "مقاس 0",
          "مقاس 1",
          "مقاس 2",
          "مقاس 3",
          "مقاس 4",
          "مقاس 5",
          "مقاس 6",
      ],
      "الطول المناسب للاعب": [
          "110 سم",
          "120 سم",
          "130 سم",
          "140 سم",
          "150 سم",
          "160 سم",
          "170 سم",
          "180 سم",
          "190 سم",
      ],
      "الفئة المستهدفة": [
          "أطفال صغار جداً",
          "أطفال",
          "أطفال / ناشئين",
          "ناشئين",
          "شباب",
          "شباب / كبار",
          "كبار",
          "كبار طوال",
          "أحجام خاصّة / كبار جداً",
      ],
  }

  guide_df = pd.DataFrame(sizes_guide)
  st.table(guide_df)
