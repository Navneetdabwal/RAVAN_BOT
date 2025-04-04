import logging
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dummy BIN and VBV data
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

# Start command
def start(update, context):
    update.message.reply_text("नमस्ते! मैं एक Educational CC Bot हूँ।\n\nCommands:\n/start\n/bininfo <BIN>\n/vbv <BIN>\n/gen <BIN>\n\nया CARD|MM|YYYY|CVV भेजो चेकिंग के लिए।")

# /bininfo command
def bin_info(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /bininfo 411111")
        return

    bin_code = context.args[0]

    if not bin_code.isdigit() or len(bin_code) != 6:
        update.message.reply_text("❌ BIN कोड 6 अंकों का और numeric होना चाहिए।")
        return

    country = BIN_DATABASE.get(bin_code, None)
    vbv_status = VBV_DATABASE.get(bin_code, None)

    if country:
        reply = f"""
BIN Info:
• BIN: `{bin_code}`
• Valid: ✅ Yes
• Country: *{country}*
• VBV Status: *{vbv_status or 'Unknown'}*
        """
    else:
        reply = f"""
BIN Info:
• BIN: `{bin_code}`
• Valid: ❌ Not Found in database
• Country: Unknown
• VBV Status: Unknown
        """

    update.message.reply_text(reply, parse_mode='Markdown')

# /vbv command
def vbv_info(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /vbv 411111")
        return

    bin_code = context.args[0]
    status = VBV_DATABASE.get(bin_code)

    if status:
        update.message.reply_text(f"BIN {bin_code} is **{status}**", parse_mode='Markdown')
    else:
        update.message.reply_text(f"BIN {bin_code} not found in database.")

# Generate Luhn-valid card
def generate_cc_from_bin(bin_code):
    cc_number = list(bin_code)
    while len(cc_number) < 15:
        cc_number.append(str(random.randint(0, 9)))

    def luhn_checksum(num_list):
        digits = [int(d) for d in num_list]
        for i in range(len(digits) - 1, -1, -2):
            doubled = digits[i] * 2
            digits[i] = doubled - 9 if doubled > 9 else doubled
        return sum(digits) % 10

    checksum = luhn_checksum(cc_number)
    last_digit = (10 - checksum) % 10
    cc_number.append(str(last_digit))
    return ''.join(cc_number)

# /gen command
def generate_card(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /gen 411111")
        return

    bin_code = context.args[0]

    if not bin_code.isdigit() or len(bin_code) != 6:
        update.message.reply_text("❌ BIN कोड 6 अंकों का होना चाहिए।")
        return

    card = generate_cc_from_bin(bin_code)
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(2026, 2030))
    cvv = str(random.randint(100, 999))

    country = BIN_DATABASE.get(bin_code, "Unknown")
    vbv_status = VBV_DATABASE.get(bin_code, "Unknown")

    update.message.reply_text(f"""
Generated Test Card (Not Real):
• Card: `{card}`
• Expiry: `{exp_month}/{exp_year}`
• CVV: `{cvv}`
• Country: *{country}*
• VBV Status: *{vbv_status}*

_This is for educational/test purposes only._
""", parse_mode='Markdown')

# Message-based CC check
def cc_checker(update, context):
    msg = update.message.text
    parts = msg.strip().split('|')
    if len(parts) == 4 and all(p.strip().isdigit() for p in parts):
        cc, mm, yyyy, cvv = parts
        bin_code = cc[:6]
        country = BIN_DATABASE.get(bin_code, "Unknown")
        vbv_status = VBV_DATABASE.get(bin_code, "Unknown")
        update.message.reply_text(f"""
Card Check:
• Card: `{cc}`
• Exp: `{mm}/{yyyy}`
• CVV: `{cvv}`
• Country: *{country}*
• VBV Status: *{vbv_status}*

*Note:* This is a fake check for demo only.
""", parse_mode='Markdown')

# Main function
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("bininfo", bin_info))
    dp.add_handler(CommandHandler("vbv", vbv_info))
    dp.add_handler(CommandHandler("gen", generate_card))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, cc_checker))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()