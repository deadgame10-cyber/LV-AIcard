import os
import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 先行啟動網頁基礎設定，確保 Streamlit 核心載入
st.set_page_config(page_title="LV 名片戰情系統 v3.3-AI", layout="wide")

# ==========================================
# 1. 初始化設定 (Firebase 雲端防禦與 Gemini)
# ==========================================
# 🚀 雲端發射脫殼版：徹底拔除 C 槽本機路徑，改為相對路徑，確保上雲端不墜機！
KEY_PATH = "serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    # 顯式指定專案名稱，確保連線指引 100% 正確
    firebase_admin.initialize_app(cred, {
        'projectId': 'goodgamelv8888',
    })

# 核心絕殺校正：嚴格對齊最新官方語法，使用 database_id="default" 穿透雲端隔離！
db = firestore.client(database_id="default")

# 最高安全防線：嚴格從秘密保險箱 (.streamlit/secrets.toml) 讀取金鑰，代碼絕不露明文
try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_KEY)
    else:
        st.error("🛑 【核心安全提示】未在秘密保險箱 (Secrets) 中找到有效的 GEMINI_API_KEY！")
except Exception as e:
    st.error(f"安全模組載入異常: {str(e)}")

# ==========================================
# 2. 核心功能：Firebase 每日次數與廣告攔截機制
# ==========================================
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

def increment_usage(user_id):
    user_ref = db.collection("users").document(user_id)
    user_ref.update({"usage_count": firestore.Increment(1)})

USER_ID = "test_user_001"
usage_count, is_vip = get_user_usage(USER_ID)

# ==========================================
# 3. 網頁前端介面：完全符合 3.2 版與圖片規格
# ==========================================
st.title("🎴 LV 名片管理與 AI 戰情分析系統 (v3.3 終極合體版)")

col_status1, col_status2 = st.columns([8, 2])
with col_status1:
    st.info(f"📊 目前每日免費分析次數：{usage_count} / 5 次")
with col_status2:
    if is_vip:
        st.success("👑 尊榮 VIP 會員")
    else:
        st.warning("⚡ 免費會員方案")

with st.form("card_form"):
    st.subheader("📝 基本資料輸入 (3.2 版格式)")
    
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("姓名")
    job_title = c2.text_input("職稱")
    company = c3.text_input("公司名稱")
    
    c4, c5 = st.columns(2)
    website = c4.text_input("公司網址 (URL)")
    email = c5.text_input("電子郵件 (E-mail)")
    
    c6, c7, c8 = st.columns(3)
    tel = c6.text_input("公司電話")
    fax = c7.text_input("公司傳真")
    mobile = c8.text_input("行動電話")
    
    st.markdown("---")
    st.subheader("📍 地址細分編碼 (3.2 版核心規範)")
    
    main_address = st.text_input("完整地址")
    
    c_add1, c_add2, c_add3 = st.columns(3)
    country = c_add1.text_input("國家", value="台灣")
    postal_code = c_add2.text_input("郵遞區號")
    city = c_add3.text_input("城市")
    
    c_add4, c_add5, c_add6 = st.columns(3)
    state = c_add4.text_input("省/直轄市/自治區")
    street = c_add5.text_input("街道")
    ext_address = c_add6.text_input("擴展地址 (如：樓層、室)")
    
    st.markdown("---")
    submit_btn = st.form_submit_button("💾 儲存名片並啟動 AI 戰情分析")

# ==========================================
# 4. 超限攔截防禦：看廣告扣次數新版格式
# ==========================================
if submit_btn:
    if usage_count >= 5 and not is_vip:
        st.error("🛑 您的每日 5 次免費 AI 戰情分析額度已達上限！")
        st.markdown("### 🔓 解鎖無限戰情分析")
        col_ad, col_pay = st.columns(2)
        
        with col_ad:
            st.markdown("#### 📺 方案 A：觀看廣告")
            st.info("觀看 15 秒廣告即可免費獲得下一次分析額度！")
            if st.button("▶️ 開始播放廣告並解鎖"):
                with st.spinner("廣告播放中... 請勿關閉網頁"):
                    import time
                    time.sleep(15)
                db.collection("users").document(USER_ID).update({"usage_count": 4})
                st.success("🎉 廣告播放完畢！已為您解鎖一次分析權限，請重新點擊上方按鈕！")
                st.rerun()
                
        with col_pay:
            st.markdown("#### 👑 方案 B：升級尊榮")
            st.success("月費 NT$ 300，解鎖無限次極速 AI 戰情分析，免看廣告！")
            if st.button("💳 立即綁卡升級尊榮會員"):
                db.collection("users").document(USER_ID).update({"is_vip": True})
                st.success("👑 感謝總指揮官支持！已成功升級為尊榮 VIP 會員，請重新點擊上方按鈕！")
                st.rerun()
                
    else:
        with st.spinner("⚔️ 戰術指揮中心正在剖析戰情，連細菌都不放過..."):
            
            prompt = f"""你是一位具有高度商業嗅覺、溫度的卓越 AI 戰情參謀長。
請針對以下輸入的名片商業資訊進行高規格的戰情剖析。

【名片對象基本資料】
- 公司：{company}
- 姓名/職稱：{name} / {job_title}
- 網址：{website}
- 郵件：{email}
- 電話/手機：{tel} / {mobile}
- 經緯定位(地址編碼)：{country} {state} {city} {street} {ext_address} (郵編: {postal_code})

請依據「KANO模型」與「商業九宮格」的獲利戰術邏輯，嚴格以繁體中文輸出以下四大戰情板塊：

一、 🎯 商業九宮格獲利邏輯深度拆解
   1. 源頭痛點：此公司或此職位在市場上面臨的最深層痛點是什麼？
   2. 收費觸發點：他們靠什麼核心價值讓客戶心甘情願掏錢？
   3. 牽引能力：他們如何綁定客戶、產生持續性的營收牽引力？

二、 📊 KANO 模型需求分類定位
   請將該公司提供的服務或產品特性，精準分類並評估其競爭力：
   1. 基本型需求 (Must-be)：他們必須做好、不做就直接被淘汰的底線是什麼？
   2. 期望型需求 (One-dimensional)：做得越多客戶越滿意的競價核心是什麼？
   3. 魅力型需求 (Attractive)：能讓客戶驚艷、瞬間翻倍、一