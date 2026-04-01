import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import img2pdf

TOKEN = os.getenv("BOT_TOKEN")

user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send images then type /done")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images:
        user_images[user_id] = []

    photo = update.message.photo[-1]
    file = await photo.get_file()

    file_path = f"{user_id}_{len(user_images[user_id])}.jpg"
    await file.download_to_drive(file_path)

    user_images[user_id].append(file_path)

    await update.message.reply_text("Image saved")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images or not user_images[user_id]:
        await update.message.reply_text("No images found")
        return

    pdf_path = f"{user_id}.pdf"

    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(user_images[user_id]))

    await update.message.reply_document(open(pdf_path, "rb"))

    for img in user_images[user_id]:
        os.remove(img)
    os.remove(pdf_path)

    user_images[user_id] = []

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("done", done))
app.add_handler(MessageHandler(filters.PHOTO, handle_image))

app.run_polling()
