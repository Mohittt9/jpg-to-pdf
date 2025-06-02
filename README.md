# Telegram JPG to PDF Converter Bot

This is a Telegram bot that allows users to send JPG images and receive a single PDF file containing those images. The bot is built using Python and leverages the `python-telegram-bot`, `Pillow`, and `fpdf` libraries.

## Features

- Accepts multiple JPG images sent by a user.
- Converts the received JPG images into a single PDF file.
- Sends the generated PDF back to the user.
- Easy to use: just send images, then type `/convert`.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Telegram account (to create and interact with your bot)
- Dependencies: `python-telegram-bot`, `Pillow`, `fpdf`

### Installation

1. **Clone the repository** (if applicable) or copy the bot script.

2. **Install dependencies:**
    ```bash
    pip install python-telegram-bot pillow fpdf
    ```

3. **Create a new bot with [BotFather](https://t.me/BotFather) on Telegram:**
    - Start a chat with BotFather and use `/newbot` to create a bot.
    - Save the API token provided.

4. **Configure your bot:**
    - Replace `YOUR_BOT_TOKEN` in the script with your actual bot token.

5. **Run the bot:**
    ```bash
    python telegram_jpg_to_pdf_bot.py
    ```

## Usage

1. Start a conversation with your bot on Telegram.
2. Send one or more JPG images to the bot.
3. Once you've sent all images, type `/convert`.
4. The bot will generate a PDF from your images and send it back to you.

## Example

```plaintext
User: (sends multiple JPG images)
User: /convert
Bot: (replies with a PDF file containing all sent images)
```

## Notes

- Only JPG images are supported by default.
- After conversion, images and generated PDFs are deleted from the server for privacy.
- You can customize the bot to support other image formats or add features.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Pillow (PIL)](https://python-pillow.org/)
- [fpdf2](https://pyfpdf.github.io/fpdf2/)
