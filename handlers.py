import os
import io
import tempfile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackQueryHandler

from PyPDF2 import PdfWriter, PdfReader
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# In-memory user session storage (for demo; replace with persistent storage for production)
user_sessions = {}

def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("convert", convert))
    app.add_handler(CommandHandler("list", list_images))
    app.add_handler(CommandHandler("remove", remove_image))
    app.add_handler(CommandHandler("move", move_image))
    app.add_handler(CommandHandler("options", set_options))
    app.add_handler(CommandHandler("title", set_title))
    app.add_handler(CommandHandler("watermark", set_watermark))
    app.add_handler(CommandHandler("addtext", add_text_page))
    app.add_handler(CommandHandler("password", set_pdf_password))
    app.add_handler(CommandHandler("upload", upload_pdf))
    app.add_handler(CommandHandler("ocr", ocr_images))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("language", set_language))
    app.add_handler(CommandHandler("startgroup", start_group))
    app.add_handler(CommandHandler("endsession", end_session))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(InlineQueryHandler(inline_query))

#######################
# Helper/session functions
#######################

def get_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "images": [],
            "pdf_options": {},
            "title": "My PDF",
            "watermark": None,
            "password": None,
            "text_pages": [],
            "language": "en"
        }
    return user_sessions[user_id]

def reset_session(user_id):
    user_sessions[user_id] = {
        "images": [],
        "pdf_options": {},
        "title": "My PDF",
        "watermark": None,
        "password": None,
        "text_pages": [],
        "language": "en"
    }

def save_image(user_id, image_bytes, filename):
    session = get_session(user_id)
    session["images"].append({
        "image": image_bytes,
        "filename": filename
    })

def get_images(user_id):
    session = get_session(user_id)
    return session["images"]

def remove_image_by_index(user_id, idx):
    session = get_session(user_id)
    if 0 <= idx < len(session["images"]):
        del session["images"][idx]
        return True
    return False

def move_image_by_index(user_id, old_idx, new_idx):
    session = get_session(user_id)
    imgs = session["images"]
    if 0 <= old_idx < len(imgs) and 0 <= new_idx < len(imgs):
        item = imgs.pop(old_idx)
        imgs.insert(new_idx, item)
        return True
    return False

def add_text_page_to_session(user_id, text):
    session = get_session(user_id)
    session["text_pages"].append(text)

def set_pdf_option(user_id, key, value):
    session = get_session(user_id)
    session["pdf_options"][key] = value

def set_pdf_title(user_id, title):
    session = get_session(user_id)
    session["title"] = title

def set_watermark_text(user_id, watermark):
    session = get_session(user_id)
    session["watermark"] = watermark

def set_pdf_password_for_user(user_id, password):
    session = get_session(user_id)
    session["password"] = password

def set_language_for_user(user_id, lang):
    session = get_session(user_id)
    session["language"] = lang

#######################
# Command Handlers
#######################

async def start(update, context):
    await update.message.reply_text(
        "👋 Welcome to JPG-to-PDF Bot!\n"
        "Send me images (JPG/PNG) and use the commands to generate customized PDFs.\n"
        "Type /help to see all features!"
    )

async def help_cmd(update, context):
    await update.message.reply_text(
        "📋 *Bot Commands and Features:*\n\n"
        "/convert - Convert your uploaded images to PDF\n"
        "/list - List your current images\n"
        "/remove <n> - Remove the nth image\n"
        "/move <from> <to> - Move image from index to another\n"
        "/options - Set PDF options (size, orientation)\n"
        "/title <title> - Set PDF document title\n"
        "/watermark <text> - Add watermark text to all pages\n"
        "/addtext <text> - Add a text-only page\n"
        "/password <pwd> - Set a password for PDF\n"
        "/upload - Upload PDF to cloud (stub)\n"
        "/ocr - Extract text from all images (OCR)\n"
        "/stats - Show your usage stats\n"
        "/language <code> - Change language (en, es, de, fr, hi)\n"
        "/startgroup - Start group session\n"
        "/endsession - Clear all your uploaded images\n"
        "Just send images or use the commands above!"
        , parse_mode="Markdown"
    )

async def convert(update, context):
    user_id = update.effective_user.id
    session = get_session(user_id)
    images = session["images"]
    text_pages = session["text_pages"]
    title = session["title"]
    watermark = session["watermark"]
    password = session["password"]

    if not images and not text_pages:
        await update.message.reply_text("❗You haven't uploaded any images or text pages yet.")
        return

    pdf_writer = PdfWriter()
    temp_files = []

    # Convert images to PDF pages
    for img_entry in images:
        img = Image.open(io.BytesIO(img_entry["image"]))
        if watermark:
            img = add_watermark_to_image(img, watermark)
        temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        img.save(temp, format="PDF")
        temp.close()
        temp_files.append(temp.name)
        pdf_writer.append(PdfReader(temp.name))

    # Add text pages if any
    for text in text_pages:
        img = text_to_image(text)
        if watermark:
            img = add_watermark_to_image(img, watermark)
        temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        img.save(temp, format="PDF")
        temp.close()
        temp_files.append(temp.name)
        pdf_writer.append(PdfReader(temp.name))

    # Set title metadata
    pdf_writer.add_metadata({
        "/Title": title
    })

    # Set password if needed
    if password:
        pdf_writer.encrypt(password)

    # Save PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out_pdf:
        pdf_writer.write(out_pdf)
        out_pdf_path = out_pdf.name

    # Clean up temp files
    for f in temp_files:
        os.unlink(f)

    # Send PDF
    with open(out_pdf_path, 'rb') as pdf_file:
        await update.message.reply_document(document=pdf_file, filename=f"{title}.pdf")
    os.unlink(out_pdf_path)

    await update.message.reply_text("✅ PDF created! Use /endsession to clear your session.")

async def list_images(update, context):
    user_id = update.effective_user.id
    images = get_images(user_id)
    text_pages = get_session(user_id)["text_pages"]
    msg = "🖼️ *Your current images/pages:*\n"
    for i, img in enumerate(images):
        msg += f"{i+1}. {img['filename']}\n"
    for i, text in enumerate(text_pages):
        msg += f"{len(images)+i+1}. [Text Page] {text[:30]}...\n"
    if not images and not text_pages:
        msg += "No images or text pages uploaded yet."
    await update.message.reply_text(msg, parse_mode="Markdown")

async def remove_image(update, context):
    user_id = update.effective_user.id
    try:
        idx = int(context.args[0]) - 1
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /remove <image_number>")
        return
    success = remove_image_by_index(user_id, idx)
    if success:
        await update.message.reply_text(f"✅ Image #{idx+1} removed.")
    else:
        await update.message.reply_text("❗Invalid image number.")

async def move_image(update, context):
    user_id = update.effective_user.id
    try:
        old_idx = int(context.args[0]) - 1
        new_idx = int(context.args[1]) - 1
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /move <from> <to>")
        return
    success = move_image_by_index(user_id, old_idx, new_idx)
    if success:
        await update.message.reply_text(f"✅ Moved image from {old_idx+1} to {new_idx+1}.")
    else:
        await update.message.reply_text("❗Invalid image numbers.")

async def set_options(update, context):
    keyboard = [
        [InlineKeyboardButton("A4", callback_data='opt_a4'),
         InlineKeyboardButton("Letter", callback_data='opt_letter')],
        [InlineKeyboardButton("Portrait", callback_data='opt_portrait'),
         InlineKeyboardButton("Landscape", callback_data='opt_landscape')]
    ]
    await update.message.reply_text(
        "Choose a PDF option (size/orientation):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_title(update, context):
    user_id = update.effective_user.id
    title = " ".join(context.args)
    if not title:
        await update.message.reply_text("Usage: /title <your pdf title>")
        return
    set_pdf_title(user_id, title)
    await update.message.reply_text(f"✅ PDF title set to: {title}")

async def set_watermark(update, context):
    user_id = update.effective_user.id
    watermark = " ".join(context.args)
    if not watermark:
        await update.message.reply_text("Usage: /watermark <text>")
        return
    set_watermark_text(user_id, watermark)
    await update.message.reply_text("✅ Watermark set.")

async def add_text_page(update, context):
    user_id = update.effective_user.id
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /addtext <your text>")
        return
    add_text_page_to_session(user_id, text)
    await update.message.reply_text("✅ Text page added.")

async def set_pdf_password(update, context):
    user_id = update.effective_user.id
    pwd = " ".join(context.args)
    if not pwd:
        await update.message.reply_text("Usage: /password <your_password>")
        return
    set_pdf_password_for_user(user_id, pwd)
    await update.message.reply_text("✅ PDF password set.")

async def upload_pdf(update, context):
    await update.message.reply_text("☁️ Uploading to cloud is not implemented in this demo.")

async def ocr_images(update, context):
    user_id = update.effective_user.id
    images = get_images(user_id)
    if not images:
        await update.message.reply_text("You haven't uploaded any images to OCR.")
        return
    results = []
    for idx, img_entry in enumerate(images):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(img_entry["image"])
            tmp.close()
            text = pytesseract.image_to_string(Image.open(tmp.name))
            results.append(f"Image {idx+1}:\n{text.strip()}")
            os.unlink(tmp.name)
    msg = "\n\n".join(results) if results else "No text detected in any image."
    await update.message.reply_text(f"📝 *OCR Results:*\n{msg}", parse_mode="Markdown")

async def show_stats(update, context):
    user_id = update.effective_user.id
    session = get_session(user_id)
    await update.message.reply_text(
        f"📊 Stats:\n"
        f"Images: {len(session['images'])}\n"
        f"Text Pages: {len(session['text_pages'])}\n"
        f"PDF Title: {session['title']}\n"
        f"Watermark: {session['watermark'] or 'None'}\n"
        f"Password: {'Set' if session['password'] else 'None'}\n"
        f"Language: {session['language']}"
    )

async def set_language(update, context):
    user_id = update.effective_user.id
    code = " ".join(context.args).strip().lower()
    valid = ["en", "es", "de", "fr", "hi"]
    if code not in valid:
        await update.message.reply_text(f"Supported languages: en, es, de, fr, hi\nUsage: /language <code>")
        return
    set_language_for_user(user_id, code)
    await update.message.reply_text(f"✅ Language set to {code}.")

async def start_group(update, context):
    await update.message.reply_text("👥 Group session feature is not implemented in this demo.")

async def end_session(update, context):
    user_id = update.effective_user.id
    reset_session(user_id)
    await update.message.reply_text("🗑️ Session cleared. All images and options reset.")

async def handle_image(update, context):
    user_id = update.effective_user.id
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        image_bytes = await file.download_as_bytearray()
        filename = f"photo_{photo.file_id}.jpg"
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        file = await update.message.document.get_file()
        image_bytes = await file.download_as_bytearray()
        filename = update.message.document.file_name or "image.jpg"
    else:
        await update.message.reply_text("Only images (JPG/PNG) are accepted!")
        return
    save_image(user_id, image_bytes, filename)
    await update.message.reply_text(f"🖼️ Image '{filename}' saved. Use /list to view or /convert to generate PDF.")

async def button_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data == 'opt_a4':
        set_pdf_option(user_id, "page_size", "A4")
        await query.answer()
        await query.edit_message_text("PDF page size set to A4.")
    elif data == 'opt_letter':
        set_pdf_option(user_id, "page_size", "Letter")
        await query.answer()
        await query.edit_message_text("PDF page size set to Letter.")
    elif data == 'opt_portrait':
        set_pdf_option(user_id, "orientation", "Portrait")
        await query.answer()
        await query.edit_message_text("PDF orientation set to Portrait.")
    elif data == 'opt_landscape':
        set_pdf_option(user_id, "orientation", "Landscape")
        await query.answer()
        await query.edit_message_text("PDF orientation set to Landscape.")
    else:
        await query.answer()
        await query.edit_message_text("Unknown option.")

async def inline_query(update, context):
    # Stub for inline queries (not implemented)
    pass

#######################
# Utility functions
#######################

def add_watermark_to_image(img, watermark_text):
    watermark = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(watermark)
    font_size = max(24, img.size[0] // 15)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    width, height = img.size
    textwidth, textheight = draw.textsize(watermark_text, font=font)
    # Centered
    x = (width - textwidth) / 2
    y = (height - textheight) / 2
    draw.text((x, y), watermark_text, fill=(255,0,0,128), font=font)
    combined = Image.alpha_composite(img.convert("RGBA"), watermark)
    return combined.convert("RGB")

def text_to_image(text):
    font_size = 36
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    lines = text.split('\n')
    width = max([font.getsize(line)[0] for line in lines]) + 40 if lines else 200
    height = font_size * len(lines) + 40 if lines else 100
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    y = 20
    for line in lines:
        draw.text((20, y), line, font=font, fill="black")
        y += font_size
    return image
