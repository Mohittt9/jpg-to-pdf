import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
from fpdf import FPDF

user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me JPG images. When done, type /convert to get a PDF.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_images:
        user_images[user_id] = []
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"{user_id}_{photo.file_id}.jpg"
    await file.download_to_drive(file_path)
    user_images[user_id].append(file_path)
    await update.message.reply_text("Image received!")

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    images = user_images.get(user_id, [])
    if not images:
        await update.message.reply_text("No images to convert!")
        return

    # Convert JPGs to PDF
    pdf = FPDF()
    for img_path in images:
        image = Image.open(img_path)
        w, h = image.size
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=pdf.w-20)
    pdf_path = f"{user_id}_output.pdf"
    pdf.output(pdf_path)

    # Send PDF
    with open(pdf_path, "rb") as pdf_file:
        await update.message.reply_document(pdf_file, filename="output.pdf")

    # Clean up
    for img in images:
        os.remove(img)
    os.remove(pdf_path)
    user_images[user_id] = []

if __name__ == '__main__':
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.run_polling()