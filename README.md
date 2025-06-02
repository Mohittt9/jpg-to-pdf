# Telegram JPG to PDF Converter Bot

A full-featured Telegram bot that converts images to PDF, with support for:
- Multiple formats (JPG, PNG, etc.)
- Image reordering, removal, preview
- Custom PDF options (page size, orientation, margins)
- Title page, watermark, text pages
- Password protection
- OCR (extract text from images)
- Cloud upload (Google Drive, Dropbox, OneDrive)
- Group sessions
- Usage stats
- Inline support
- Multilingual interface

## Quick Start

1. Clone the repo and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Set your Telegram Bot token in `config.py`.
3. Run:
    ```bash
    python bot.py
    ```

## Features & Commands

- `/start` - Start the bot
- `/help` - List all features and usage
- `/convert` - Convert images to PDF
- `/list` - Preview uploaded images
- `/remove <n>` - Remove image by index
- `/move <from> <to>` - Reorder images
- `/options` - PDF options (page size, orientation, etc.)
- `/title <text>` - Add title page
- `/watermark <text>` - Add watermark
- `/addtext <text>` - Add text-only page
- `/password <pass>` - Set PDF password
- `/upload` - Upload PDF to cloud
- `/ocr` - Extract text from images (OCR)
- `/stats` - Usage statistics
- `/language <code>` - Change language
- `/startgroup` - Start a group PDF session
- `/endsession` - End the current session

## Contributing

Contributions are welcome! See individual modules for TODOs.

## License

MIT License