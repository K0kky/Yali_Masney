import discord
import asyncio
import os
from datetime import datetime, time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# =====================
TARGET_USER_ID = 123456789012345678  # 対象ユーザーのID
CHANNEL_ID = 987654321098765432     # メッセージ送信チャンネルID
MENTION_WORD = "起きてますか？"      # メンション時のワード
START_TIME = time(9, 0)             # 開始時刻（09:00）
END_TIME = time(23, 0)              # 終了時刻（23:00）
INTERVAL = 600                      # 10分（600秒）
# =======================

intents = discord.Intents.default()
intents.presences = True  
intents.members = True    

client = discord.Client(intents=intents)

user_online = False
task_running = False

async def mention_loop():
    global user_online, task_running
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    user = await client.fetch_user(TARGET_USER_ID)

    while True:
        now = datetime.now().time()
        if START_TIME <= now <= END_TIME:
            member = channel.guild.get_member(TARGET_USER_ID)
            if member and member.status == discord.Status.online:
                if not task_running:
                    print(f"{member.display_name} がオンラインになったのでメンションを開始します。")
                    task_running = True
                    while member.status == discord.Status.online and START_TIME <= datetime.now().time() <= END_TIME:
                        await channel.send(f"{user.mention} {MENTION_WORD}")
                        await asyncio.sleep(INTERVAL)
                    print("ユーザーがオフラインになったか、時間外になったため停止。")
                    task_running = False
        await asyncio.sleep(30)  # チェック間隔（30秒）
        
@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    client.loop.create_task(mention_loop())

client.run(TOKEN)
