import discord
from discord.ext import commands, tasks
import asyncio
import datetime

TOKEN = "YOUR_BOT_TOKEN"
TARGET_USER_ID = 123456789012345678  
CHANNEL_ID = 987654321098765432      

START_HOUR = 18
END_HOUR = 23

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


user_online = False

message_task = None

def is_in_time_range():
    now = datetime.datetime.now().time()
    start = datetime.time(START_HOUR, 0, 0)
    end = datetime.time(END_HOUR, 0, 0)
    # 時間帯判定（start <= now < end）
    if start <= now < end:
        return True
    else:
        return False

async def send_periodic_message(channel, user):
    while True:     
        await asyncio.sleep(600)
        if not is_in_time_range():
            print("時間外のためメッセージ送信停止")
            break
        member = channel.guild.get_member(user.id)
        if member is None or member.status == discord.Status.offline:
            print("ユーザーがオフラインのためメッセージ送信停止")
            break
        try:
            await channel.send(f"{user.mention} ここに特定のメッセージを入れてください！")
            print("メッセージ送信")
        except Exception as e:
            print(f"送信失敗: {e}")

@bot.event
async def on_ready():
    print(f"Bot 起動完了: {bot.user}")

@bot.event
async def on_presence_update(before, after):
    global user_online, message_task

    if after.id != TARGET_USER_ID:
        return

    if not is_in_time_range():
        return

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("指定チャンネルが見つかりません")
        return

    # オンラインになったら
    if after.status != discord.Status.offline and (before.status == discord.Status.offline or before.status is None):
        print(f"{after.name} がオンラインになりました")
        user_online = True

        # すでにタスクが動いてたらキャンセルしてから作り直す
        if message_task is not None and not message_task.done():
            message_task.cancel()
            print("既存のメッセージタスクをキャンセル")

        message_task = bot.loop.create_task(send_periodic_message(channel, after))
    
    # オフラインになったら
    elif after.status == discord.Status.offline and before.status != discord.Status.offline:
        print(f"{after.name} がオフラインになりました")
        user_online = False
        if message_task is not None and not message_task.done():
            message_task.cancel()
            print("メッセージタスクをキャンセルしました")

bot.run(TOKEN)
