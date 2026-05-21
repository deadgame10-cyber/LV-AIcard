import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import google.generativeai as genai

# --- 初始化設定 ---
st.set_page_config(page_title="LV 名片戰情系統 v3.3-AI", layout="wide")

# Firebase 初始化
KEY_PATH = "serviceAccountKey.json"
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred, {'projectId': 'goodgamelv8888'})
    except Exception as e:
        st.error(f"Firebase 初始化失敗: {str(e)}")

db = firestore.client(database_id="default")

# --- 安全讀取金鑰 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("●【核心安全提示】未找到有效的 GEMINI_API_KEY！")
    model = None

# --- 功能函數 ---
def get_user_usage(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    user_ref = db.collection("users").document(user_id)
    doc = user_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if data.get("last_active_date") == today:
            return data.get("usage_count", 0), data.get("is_vip", False)
        else:
            user_ref.update({"usage_count": 0, "last_active_date": today})
            return 0, data.get("is_vip", False)
    else:
        user_ref.set({"usage_count": 0, "last_active_date": today, "is_vip": False})
        return 0, False

USER_ID = "test_user_001"
usage_count, is_vip = get_user_usage(USER_ID)

# --- 網頁前端介面 ---
st.title("▣ LV 名片管理與 AI 戰情分析系統 (v3.3 終極合體版)")

col_status1, col_status2 = st.columns([8, 2])
with col_status1:
    st.info("▣ 目前每日免費分析次數：" + str(usage_count) + " / 5 次")
with col_status2:
    st.success("VIP 會員" if is_vip else "⚡ 免費會員方案")

with st.form("card_form"):
    st.subheader("▣ 基本資料輸入")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("姓名")
    job_title = c2.text_input("職稱")
    company = c3.text_input("公司名稱")

    c4, c5 = st.columns(2)
    website = c4.text_input("公司網址 (URL)")
    email = c5.text_input("電子郵件 (E-mail)")

    st.markdown("---")
    st.subheader("▣ 地址細分編碼 (3.2 版核心規範)")
    country = st.text_input("國家", value="台灣")
    c_add1, c_add2, c_add3 = st.columns(3)
    postal_code = c_add1.text_input("郵遞區號")
    city = c_add2.text_input("城市")
    state = c_add3.text_input("省/直轄市/自治區")
    
    c_add4, c_add5 = st.columns(2)
    street = c_add4.text_input("街道")
    ext_address = c_add5.text_input("擴展地址 (如：樓層、室)")

    submit_btn = st.form_submit_button("▣ 儲存名片並啟動 AI 戰情分析")

if submit_btn:
    if usage_count >= 5 and not is_vip:
        st.error("本日分析次數已達上限，請觀看廣告或升級 VIP。")
    elif model:
        st.write("正在啟動 AI 深度戰情分析...")
        # 穩定拼接 AI 提示詞
        full_prompt = "你是一位具有高度商業嗅覺、溫度的卓越 AI 戰情參謀長。"
        full_prompt += "請對以下名片資料進行深度分析：姓名-" + name + "，公司-" + company + "，國家-" + country + "，城市-" + city
        
        response = model.generate_content(full_prompt)
        st.markdown("### ▣ AI 戰情分析報告")
        st.write(response.text)
        
        # 次數累加
        db.collection("users").document(USER_ID).update({"usage_count": usage_count + 1})
        st.success("分析已完成，扣除 1 次額度。")
    
