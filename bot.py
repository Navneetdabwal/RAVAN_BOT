import os
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Fake BIN & VBV database
BIN_DATABASE = {
    "411111": "United States",
    "510510": "Canada",
    "520082": "India",
    "530090": "Brazil"
}

VBV_DATABASE = {
    "411111": "NON-VBV",
    "510510": "VBV",
    "520082": "NON-VBV",
    "530090": "VBV"
}

# Init bot and Flask app
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Dispatcher setup
dispatcher = Dispatcher(bot, None, use_context=True)

# Handlers
def start(update, context):
    update.message.reply_text("नमस्ते! मैं CC Bot हूँ। Commands:\n/start\n/bininfo <bin>\n/vbv <bin>\n/gen <bin>\n\nया Card भेजो इस फॉर्मेट में: `4111111234567890|04|2026|123`")

def bininfo(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /bininfo 411111")
        return
    bin_code = context.args[0]
    country = BIN_DATABASE.get(bin_code)
    vbv = VBV_DATABASE.get(bin_code)
    if country:
        update.message.reply_text(f"BIN: {bin_code}\nValid: ✅\nCountry: {country}\nVBV: {vbv}")
    else:
        update.message.reply_text(f"BIN: {bin_code}\nValid: ❌ Not Found")

def vbv(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /vbv 411111")
        return
    bin_code = context.args[0]
    vbv_status = VBV_DATABASE.get(bin_code, "Unknown")
    update.message.reply_text(f"VBV Status for {bin_code}: {vbv_status}")

def generate_cc_from_bin(bin_code):
    cc_number = list(bin_code)
    while len(cc_number) < 15:
        cc_number.append(str(random.randint(0, 9)))

    def luhn_checksum(num_list):
        digits = [int(d) for d in num_list]
        for i in range(len(digits)-2, -1, -2):
            doubled = digits[i] * 2
            digits[i] = doubled - 9 if doubled > 9 else doubled
        return sum(digits) % 10

    checksum = luhn_checksum(cc_number)
    last_digit = (10 - checksum) % 10
    cc_number.append(str(last_digit))
    return ''.join(cc_number)

def gen(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /gen 411111")
        return
    bin_code = context.args[0]
    if not bin_code.isdigit() or len(bin_code) != 6:
        update.message.reply_text("BIN 6 digit numeric होना चाहिए")
        return

    card = generate_cc_from_bin(bin_code)
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(2025, 2030))
    cvv = str(random.randint(100, 999))
    country = BIN_DATABASE.get(bin_code, "Unknown")
    vbv_status = VBV_DATABASE.get(bin_code, "Unknown")

    update.message.reply_text(f"""
Generated Card:
Card: {card}
Expiry: {exp_month}/{exp_year}
CVV: {cvv}
Country: {country}
VBV: {vbv_status}
    """)

def cc_check(update, context):
    text = update.message.text.strip()
    if '|' not in text: return
    parts = text.split('|')
    if len(parts) != 4: return
    cc, mm, yy, cvv = parts
    if len(cc) < 6: return
    bin_code = cc[:6]
    country = BIN_DATABASE.get(bin_code, "Unknown")
    vbv = VBV_DATABASE.get(bin_code, "Unknown")
    update.message.reply_text(f"""
Card Check:
Card: {cc}
Exp: {mm}/{yy}
CVV: {cvv}
Country: {country}
VBV: {vbv}
    """)

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("bininfo", bininfo))
dispatcher.add_handler(CommandHandler("vbv", vbv))
dispatcher.add_handler(CommandHandler("gen", gen))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, cc_check))

# Flask routes
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def home():
    return 'Bot is live.'

# Set webhook on startup
if __name__ == "__main__":
    bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
