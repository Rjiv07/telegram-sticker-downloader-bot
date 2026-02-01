import os, re, zipfile, asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

# ==============================
# ENV VARIABLES (IMPORTANT)
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")            # set in Railway / local export
API_ID = int(os.getenv("API_ID"))             # must be int
API_HASH = os.getenv("API_HASH")

# ==============================
# FOLDERS
# ==============================
BASE_DIR = "downloads"
os.makedirs(BASE_DIR, exist_ok=True)

# ==============================
# TELETHON CLIENT
# ==============================
tg = TelegramClient("user_session", API_ID, API_HASH)

# ==============================
# DOWNLOAD FUNCTION
# ==============================
async def download_pack(pack_name):
    await tg.start()

    result = await tg(GetStickerSetRequest(
        stickerset=InputStickerSetShortName(pack_name),
        hash=0
    ))

    pack_dir = os.path.join(BASE_DIR, pack_name)
    os.makedirs(pack_dir, exist_ok=True)

    for doc in result.documents:
        await tg.download_media(doc, pack_dir)

    zip_path = pack_dir + ".zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in os.listdir(pack_dir):
            z.write(os.path.join(pack_dir, f), f)

    return zip_path

# ==============================
# BOT HANDLER
# ==============================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    match = re.search(r"addstickers/([A-Za-z0-9_]+)", text)
    if not match:
        await update.message.reply_text(
            "❌ Paste a sticker pack link\n\nExample:\nhttps://t.me/addstickers/Cats"
        )
        return

    pack_name = match.group(1)
    await update.message.reply_text("⏳ Downloading sticker pack...")

    try:
        zip_file = await download_pack(pack_name)

        await update.message.reply_document(
            document=open(zip_file, "rb"),
            filename=f"{pack_name}.zip"
        )

    except Exception as e:
        await update.message.reply_text("⚠️ Failed to download pack")
        print("ERROR:", e)

# ==============================
# START BOT
# ==============================
def main():
    print("🤖 Bot started and waiting for links...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.run_polling()

if __name__ == "__main__":
    main()
