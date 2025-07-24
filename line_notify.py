from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime

# 🔐 換成你自己的 Line Bot Token
LINE_CHANNEL_ACCESS_TOKEN = '20f321113048e5b17c5c8eeeef6ca4f9'
LINE_USER_ID = '2007808331'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def notify_member_login(member_name, total_spent):
    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    message = f"""🎉 會員登入成功！
會員名稱：{member_name}
登入時間：{now}
今日消費累積：${total_spent}"""

    try:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=message)
        )
        print("✅ Line Bot 推播成功")
    except Exception as e:
        print(f"❌ Line Bot 發送失敗：{e}")
