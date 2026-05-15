import zipfile
import os

# core 展開
if os.path.exists("こあのじっぷ.zip") and not os.path.exists("bcsfe/core"):
    with zipfile.ZipFile("こあのじっぷ.zip", "r") as z:
        z.extractall("bcsfe")

# cli 展開
if os.path.exists("cli.zip") and not os.path.exists("bcsfe/cli"):
    with zipfile.ZipFile("cli.zip", "r") as z:
        z.extractall("bcsfe")
        import zipfile
import os

# core 展開
if os.path.exists("こあのじっぷ.zip") and not os.path.exists("bcsfe/core"):
    with zipfile.ZipFile("こあのじっぷ.zip", "r") as z:
        z.extractall("bcsfe")

# cli 展開
if os.path.exists("cli.zip") and not os.path.exists("bcsfe/cli"):
    with zipfile.ZipFile("cli.zip", "r") as z:
        z.extractall("bcsfe")
        
import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import traceback
from datetime import datetime
from dotenv import load_dotenv

# ======================================================
# 🔹 環境変数読み込み
# ======================================================
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("⚠️ .env ファイルが見つかりません。")

TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_BOT_TOKEN")
GLOBAL_LOG_CHANNEL_ID = int(os.getenv("GLOBAL_LOG_CHANNEL_ID", 0))
DISCORD_CHANNEL = os.getenv("DISCORD_CHANNEL")

# ★追加：特定の管理用サーバーIDを読み込む
guild_id_env = os.getenv("MY_GUILD_ID")
MY_GUILD_ID = int(guild_id_env) if guild_id_env else 1503705749606367294

if not TOKEN:
    raise RuntimeError("❌ .env に TOKEN が設定されていません。")

# ======================================================
# 🔹 BOT 初期化
# ======================================================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ======================================================
# 🔹 管理者チェック（Slash用）
# ======================================================
def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        raise app_commands.CheckFailure("このコマンドは管理者のみ使用できます。")
    return app_commands.check(predicate)

# ======================================================
# 🔹 Cog 自動ロード
# ======================================================
async def load_all_cogs():
    print("===================================")
    print("🧩 --- Cog 自動ロード開始 ---")

    base_dir = os.path.join(os.path.dirname(__file__), "cogs")

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for file in os.listdir(base_dir):
        if not file.endswith(".py") or file.startswith("__"):
            continue

        cog_name = file[:-3]
        try:
            await bot.load_extension(f"cogs.{cog_name}")
            print(f"✅ Loaded: cogs.{cog_name}")
        except commands.errors.NoEntryPointError:
            print(f"⚠ setup() が無いためスキップ: {cog_name}")
        except discord.ClientException as e:
            print(f"⚠ 既にロード済み: {cog_name} ({e})")
        except Exception:
            print(f"❌ Failed: {cog_name}")
            traceback.print_exc()

    print("🧩 --- Cog 自動ロード完了 ---")

# ======================================================
# 🔹 グローバルログ送信
# ======================================================
async def send_global_log(embed: discord.Embed):
    if GLOBAL_LOG_CHANNEL_ID:
        channel = bot.get_channel(GLOBAL_LOG_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

@bot.event
async def on_guild_join(guild: discord.Guild):
    embed = discord.Embed(
        title="🟢 Botが新しいサーバーに参加しました！",
        description=f"**サーバー名:** {guild.name}\n**ID:** `{guild.id}`\n**メンバー数:** `{guild.member_count}`",
        color=discord.Color.green(),
        timestamp=datetime.utcnow(),
    )
    await send_global_log(embed)

@bot.event
async def on_guild_remove(guild: discord.Guild):
    embed = discord.Embed(
        title="🔴 Botがサーバーから退出しました",
        description=f"**サーバー名:** {guild.name}\n**ID:** `{guild.id}`",
        color=discord.Color.red(),
        timestamp=datetime.utcnow(),
    )
    await send_global_log(embed)

# ======================================================
# 🔹 ステータス更新ループ
# ======================================================
async def update_activity():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await bot.change_presence(
            activity=discord.Game(f"にゃんこ大戦争自動代行"),
            status=discord.Status.online
        )
        await asyncio.sleep(3600)

# ======================================================
# 🔹 起動処理とコマンド同期
# ======================================================
@bot.event
async def setup_hook():
    await load_all_cogs()
    try:
        # 1. 全サーバー共通のコマンドを同期
        synced = await bot.tree.sync()
        print(f"🌳 グローバルコマンド同期完了！({len(synced)}件)")

        # 2. ★追加：管理用サーバー専用のコマンドを同期
        if MY_GUILD_ID:
            MY_GUILD = discord.Object(id=MY_GUILD_ID)
            guild_synced = await bot.tree.sync(guild=MY_GUILD)
            print(f"🏰 管理サーバー専用コマンド同期完了！({len(guild_synced)}件)")

    except Exception as e:
        print(f"⚠️ スラッシュコマンド同期エラー: {e}")
    
    print("===================================")

@bot.event
async def on_ready():
    print("===================================")
    print(f"Bot logged in as {bot.user}")
    print("===================================")

    if not any(task.get_name() == "update_activity" for task in asyncio.all_tasks()):
        bot.loop.create_task(update_activity(), name="update_activity")

    if DISCORD_CHANNEL:
        channel = bot.get_channel(int(DISCORD_CHANNEL))
        if channel:
            embed = discord.Embed(
                title="🚀 Bot起動完了",
                description=f"{bot.user} がオンラインになりました！",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            await channel.send(embed=embed)

# ======================================================
# 🔹 スラッシュコマンドエラーハンドラ
# ======================================================
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        # ★修正: 既に utils.py 側で「製作者のみ～」と返信済みの場合は何もしない（二重メッセージ防止）
        if not interaction.response.is_done():
            await interaction.response.send_message("🚫 権限がありません。", ephemeral=True)
        return
    
    if isinstance(error, app_commands.CommandInvokeError):
        original = getattr(error, "original", None)
        if isinstance(original, discord.errors.HTTPException) and original.code in (40060, 10062):
            return

    print(f"⚠️ スラッシュコマンドエラー: {error}")
    traceback.print_exc()

# ======================================================
# 🔹 手動再同期コマンド
# ======================================================
@bot.command()
@commands.is_owner()
async def sync(ctx):
    # 手動同期時も管理用サーバーを同期するように修正
    await bot.tree.sync()
    if MY_GUILD_ID:
        MY_GUILD = discord.Object(id=MY_GUILD_ID)
        await bot.tree.sync(guild=MY_GUILD)
    await ctx.send("✅ スラッシュコマンドを再同期しました。")
    print("🔄 手動スラッシュコマンド同期完了。")

# ======================================================
# 🔹 BOT 起動
# ======================================================
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 手動停止されました。")
    except Exception:
        traceback.print_exc()