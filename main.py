import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime, time
from aiohttp import web

# =================== 設定 ===================
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN が設定されていません")

GUILD_ID = 1114257918850760795  # 固定ギルドID
CHANNEL_ID = 1390661811967361094  # 通知するチャンネルID（適宜書き換えて）
TARGET_USER_ID = 927414765280694283  # 監視対象ユーザーID（書き換え）

MENTION_WORD = "寝ろスギ"  # メンションワード
START_TIME = time(23, 0)   # 開始時刻（9:00）
END_TIME = time(0, 0)    # 終了時刻（23:00）
INTERVAL = 300            # メッセージ間隔（秒）＝10分
# ============================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

task_running = False

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    bot.loop.create_task(monitor_user_status())

# 監視ループ
async def monitor_user_status():
    global task_running
    await bot.wait_until_ready()
    await asyncio.sleep(5)  # 起動直後の準備

    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(CHANNEL_ID)

    while True:
        now = datetime.now().time()
        if START_TIME <= now <= END_TIME:
            member = guild.get_member(TARGET_USER_ID)
            if member and member.status == discord.Status.online:
                if not task_running:
                    print(f"🟢 {member.display_name} がオンラインになりました")
                    task_running = True
                    while member.status == discord.Status.online and START_TIME <= datetime.now().time() <= END_TIME:
                        await channel.send(f"<@{TARGET_USER_ID}> {MENTION_WORD}")
                        await asyncio.sleep(INTERVAL)
                    print("🔴 オフライン or 時間外、通知停止")
                    task_running = False
        await asyncio.sleep(30)  # 状態チェック間隔

# ============ 簡易Webサーバー（Render用） ============
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port=int(os.getenv("PORT", 8080)))
    await site.start()
    print("🌐 keep-aliveサーバー起動中")

# ================== 実行部 ==================
async def main():
    await start_web_server()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
