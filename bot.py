import os
from flask import Flask, request
import telebot
import requests
import random


API_TOKEN = os.getenv("BOT_TOKEN")  # Set BOT_TOKEN in environment variable
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to RAVAN_BOT!\nUse /help to see available commands.\nCreated by: 𝙉𝘼𝙑𝙉𝙀𝙀𝙏 𝘿𝘼𝘽𝙒𝘼𝙇")

# /help command
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """*Available Commands:*

/chk - Check a single CC
/mass - Check multiple CCs
/gen or /gnt - Generate 15 random CCs using a BIN
/bin - Get BIN info (validity, country, bank)
/bininfo - Detailed BIN validation
/vbv - Check if BIN is VBV or Non-VBV
/fake - Get fake user info from a country


/vvb - 3D Secure check
/validate <cc> - Validate card using Luhn + BIN + length
/custom <bin> - Custom BIN Generator
/test <cc> - Simulate live test result


_Created by: 𝙉𝘼𝙑𝙉𝙀𝙀𝙏 𝘿𝘼𝘽𝙒𝘼𝙇_"""
    bot.reply_to(message, help_text, parse_mode='Markdown')





def generate_cc(bin_format):
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10

    def complete_number(bin_part):
        number = bin_part
        while len(number) < 15:
            number += str(random.randint(0,9))
        for check_digit in range(10):
            candidate = number + str(check_digit)
            if luhn_checksum(candidate) == 0:
                return candidate
        return None

    cc_list = []
    for _ in range(15):
        cc_number = complete_number(bin_format)
        if cc_number:
            mm = str(random.randint(1, 12)).zfill(2)
            yyyy = str(random.randint(2025, 2030))
            cvv = str(random.randint(100, 999))
            cc_list.append(f"{cc_number}|{mm}|{yyyy}|{cvv}")
    return cc_list

@bot.message_handler(commands=['gnt', 'gen'])
def handle_generate(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /gnt <BIN>\nExample: /gnt 545230")
            return
        bin_code = parts[1]
        if not bin_code.isdigit() or len(bin_code) < 6:
            bot.reply_to(message, "Invalid BIN. Please provide at least 6 digits.")
            return
        cards = generate_cc(bin_code)
        bot.reply_to(message, "Generated Cards:\n" + "\n".join(cards))
    except Exception as e:
        bot.reply_to(message, "Error generating cards.")






def generate_credit_card(bin_format):
    bin_format = bin_format.replace('x', 'X')
    cc_number = ''
    for char in bin_format:
        if char == 'X':
            cc_number += str(random.randint(0, 9))
        else:
            cc_number += char

    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(2025, 2030))

    # Determine card type and CVV length
    if cc_number.startswith('34') or cc_number.startswith('37'):
        # Amex
        cvv = str(random.randint(1000, 9999))
    else:
        cvv = str(random.randint(100, 999))

    return f"{cc_number}|{month}|{year}|{cvv}"

# Example use:
bin_input = "378282XXXXXX"  # Amex BIN example
print(generate_credit_card(bin_input))




@bot.message_handler(commands=['gen', 'gnt'])
def handle_generate(message):
    try:
        bin_input = message.text.split()[1]
        cc_detail = generate_credit_card(bin_input)
        bot.reply_to(message, f"`{cc_detail}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "Usage: /gen 545231XXXXXXXXXX", parse_mode="Markdown")






# /chk command
@bot.message_handler(commands=['chk'])
def check_single_cc(message):
    try:
        cc = message.text.split()[1]
        # Dummy validation (Replace with real checker API)
        result = "Live ✅" if cc.endswith("2") else "Dead ❌"
        bot.reply_to(message, f"CC: {cc}\nStatus: {result}")
    except:
        bot.reply_to(message, "Use like: /chk 4147201234567890|12|2025|123")




def luhn_checksum(card_number):
    def digits_of(n): return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd = digits[-1::-2]
    even = digits[-2::-2]
    return (sum(odd) + sum([sum(digits_of(d*2)) for d in even])) % 10 == 0

@bot.message_handler(commands=['validate'])
def validate_cc(message):
    try:
        cc = message.text.split()[1].replace(" ", "")
        if not cc.isdigit():
            return bot.reply_to(message, "Invalid CC format.")
        if len(cc) < 13 or len(cc) > 19:
            return bot.reply_to(message, "Invalid CC length.")
        result = "Valid" if luhn_checksum(cc) else "Invalid"
        bot.reply_to(message, f"Card: {cc}\nLuhn: {result}")
    except:
        bot.reply_to(message, "Usage: /validate <cc>")




@bot.message_handler(commands=['custom'])
def custom_bin_gen(message):
    try:
        bin_input = message.text.split()[1]
        if not bin_input.isdigit() or len(bin_input) < 6:
            return bot.reply_to(message, "Invalid BIN.")
        generated = generate_card(bin_input)
        bot.reply_to(message, f"Generated: {generated}")
    except:
        bot.reply_to(message, "Usage: /custom <bin>")

def generate_card(bin_str):
    import random
    length = 15 if bin_str.startswith('3') else 16
    cc = bin_str
    while len(cc) < (length - 1):
        cc += str(random.randint(0, 9))
    checksum = [int(x) for x in cc]
    total = sum(checksum[-1::-2]) + sum([sum(divmod(2 * x, 10)) for x in checksum[-2::-2]])
    cc += str((10 - (total % 10)) % 10)
    mm = f"{random.randint(1, 12):02d}"
    yy = str(random.randint(2025, 2030))
    cvv_len = 4 if cc.startswith("34") or cc.startswith("37") else 3
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(cvv_len)])
    return f"{cc}|{mm}|{yy}|{cvv}"





@bot.message_handler(commands=['test'])
def fake_test_result(message):
    try:
        cc = message.text.split()[1]
        if not cc or not cc.replace(" ", "").isdigit():
            return bot.reply_to(message, "Invalid CC.")
        import random
        statuses = ['Approved', 'Declined', 'Insufficient Funds', 'CVV Mismatch', 'Expired']
        result = random.choice(statuses)
        bot.reply_to(message, f"Testing {cc}...\nResult: {result}")
    except:
        bot.reply_to(message, "Usage: /test <cc>")





# /mass command
@bot.message_handler(commands=['mass'])
def check_mass_cc(message):
    try:
        lines = message.text.split("\n")[1:]
        if not lines:
            bot.reply_to(message, "Please input minimum 15 CCs after /mass")
            return
        results = []
        for cc in lines:
            status = "Live ✅" if cc.strip().endswith("2") else "Dead ❌"
            results.append(f"{cc.strip()} - {status}")
        bot.reply_to(message, "\n".join(results))
    except:
        bot.reply_to(message, "Please enter CCs properly after /mass")

# /bin or /bininfo
@bot.message_handler(commands=['bin', 'bininfo'])
def bin_lookup(message):
    try:
        bin_code = message.text.split()[1]
        response = requests.get(f"https://lookup.binlist.net/{bin_code}")
        if response.status_code == 200:
            data = response.json()
            info = f"""
*BIN Info:*
BIN: {bin_code}
Scheme: {data.get('scheme', 'N/A')}
Type: {data.get('type', 'N/A')}
Brand: {data.get('brand', 'N/A')}
Bank: {data.get('bank', {}).get('name', 'N/A')}
Country: {data.get('country', {}).get('name', 'N/A')}
Valid: ✅
"""
        else:
            info = f"BIN {bin_code} is Invalid ❌"
        bot.reply_to(message, info, parse_mode='Markdown')
    except:
        bot.reply_to(message, "Use like: /bin 414720")

# /vbv command
@bot.message_handler(commands=['vbv'])
def vbv_check(message):
    try:
        bin_code = message.text.split()[1]
        # Dummy logic: You can replace with real API
        vbv_status = "VBV ✅" if bin_code.endswith("0") else "Non-VBV ❌"
        bot.reply_to(message, f"BIN: {bin_code}\nVBV Status: {vbv_status}")
    except:
        bot.reply_to(message, "Use like: /vbv 414720")














from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from faker import Faker
import pycountry

user_sessions = {}

# /fake command handler
@bot.message_handler(commands=['fake'])
def send_country_selection(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    countries = list(pycountry.countries)
    buttons = [InlineKeyboardButton(text=country.name, callback_data=f"fake_{country.alpha_2}") for country in countries[:99]]
    keyboard.add(*buttons)
    msg = bot.send_message(message.chat.id, "🌍 Choose a country to generate a fake identity:", reply_markup=keyboard)
    user_sessions[message.chat.id] = msg.message_id  # Store message ID to delete it later

# Callback handler for country selection
@bot.callback_query_handler(func=lambda call: call.data.startswith('fake_'))
def handle_country_callback(call: CallbackQuery):
    code = call.data.split('_')[1]
    faker = Faker(code.lower())

    name = faker.name()
    address = faker.address().replace("\n", ", ")
    phone = faker.phone_number()
    email = faker.email()
    city = faker.city()
    postcode = faker.postcode()
    state = faker.state() if hasattr(faker, 'state') else 'N/A'

    result = (
        f"🕵️‍♂️ *Fake Identity for {pycountry.countries.get(alpha_2=code).name}*\n\n"
        f"*Name:* `{name}`\n"
        f"*Email:* `{email}`\n"
        f"*Phone:* `{phone}`\n"
        f"*Address:* `{address}`\n"
        f"*City:* `{city}`\n"
        f"*District/State:* `{state}`\n"
        f"*Postal Code:* `{postcode}`"
    )

    # Delete previous country selection message
    try:
        bot.delete_message(call.message.chat.id, user_sessions.get(call.message.chat.id, call.message.message_id))
    except:
        pass

    bot.send_message(call.message.chat.id, result, parse_mode='Markdown')











# Webhook route
@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "RAVAN_BOT is Running!"

@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Set webhook once app starts
@app.before_first_request
def setup_webhook():
    webhook_url = f"https://ravan-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))











# main.py - Combined BINVERSE + FAKEID++ Telegram Bot
from flask import Flask, request
import requests
import random
from faker import Faker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, Updater, CallbackQueryHandler
import os

app = Flask(__name__)
TOKEN = os.environ.get("BOT_TOKEN")
fake = Faker()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# BIN CHECKER
def bin_command(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Use: /bin <BIN>")
        return
    bin_number = context.args[0]
    res = requests.get(f"https://lookup.binlist.net/{bin_number}")
    if res.status_code != 200:
        update.message.reply_text("BIN not found or invalid.")
        return
    data = res.json()
    msg = f"**BIN Info:**\n\n"
    msg += f"**Scheme:** {data.get('scheme', 'N/A')}\n"
    msg += f"**Type:** {data.get('type', 'N/A')}\n"
    msg += f"**Brand:** {data.get('brand', 'N/A')}\n"
    msg += f"**Bank:** {data.get('bank', {}).get('name', 'N/A')}\n"
    msg += f"**Country:** {data.get('country', {}).get('name', 'N/A')}\n"
    update.message.reply_text(msg, parse_mode="Markdown")

# RISK SCORE
def risk_command(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Use: /risk <BIN>")
        return
    score = random.randint(1, 100)
    level = "LOW"
    if score > 70:
        level = "HIGH"
    elif score > 40:
        level = "MEDIUM"
    update.message.reply_text(f"**BIN Risk Score:** {score}/100\nLevel: {level}", parse_mode="Markdown")

# DARK WEB CHECK (Simulated)
def darkweb_command(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Use: /darkweb <BIN>")
        return
    found = random.choice([True, False])
    msg = "âš ï¸ BIN Found on Dark Web!" if found else "âœ… BIN Not found on Dark Web."
    update.message.reply_text(msg)

# CREDIT LIMIT PREDICTOR
def limit_command(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("Use: /limit <BIN>")
        return
    limit = random.choice(["$500-$1500", "$2000-$5000", "$5000-$10,000", "$10,000+"])
    update.message.reply_text(f"Estimated Credit Limit: {limit}")

# CUSTOM BIN GENERATOR
def custombin_command(update: Update, context: CallbackContext):
    if len(context.args) < 4:
        update.message.reply_text("Use: /custombin <bin> <mm> <yyyy> <cvv_len>")
        return
    bin_prefix, mm, yyyy, cvv_len = context.args[:4]
    num = bin_prefix + "".join([str(random.randint(0,9)) for _ in range(16-len(bin_prefix))])
    cvv = "".join([str(random.randint(0,9)) for _ in range(int(cvv_len))])
    update.message.reply_text(f"{num}|{mm}|{yyyy}|{cvv}")

# COUNTRY BIN GRAPH SIMULATED
def bingraph_command(update: Update, context: CallbackContext):
    update.message.reply_text("Country-wise BIN Graph coming soon with chart image!")

# --- FAKEID++ PART ---

countries = {
    "US": "United States",
    "IN": "India",
    "UK": "United Kingdom",
    "AU": "Australia",
    "CA": "Canada"
}

def fake_command(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(name, callback_data=code)] for code, name in countries.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select a country:", reply_markup=reply_markup)

def generate_fake_identity(code):
    Faker.seed(random.randint(1000,9999))
    fake = Faker()
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    address = fake.address().replace("\n", ", ")
    city = fake.city()
    zip_code = fake.postcode()
    return f"**{countries[code]} Fake ID:**\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\nCity: {city}\nZIP: {zip_code}"

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    code = query.data
    msg = generate_fake_identity(code)
    context.bot.send_message(chat_id=query.message.chat_id, text=msg, parse_mode="Markdown")
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

# Registering all handlers
dispatcher.add_handler(CommandHandler("bin", bin_command))
dispatcher.add_handler(CommandHandler("risk", risk_command))
dispatcher.add_handler(CommandHandler("darkweb", darkweb_command))
dispatcher.add_handler(CommandHandler("limit", limit_command))
dispatcher.add_handler(CommandHandler("custombin", custombin_command))
dispatcher.add_handler(CommandHandler("bingraph", bingraph_command))
dispatcher.add_handler(CommandHandler("fake", fake_command))
dispatcher.add_handler(CallbackQueryHandler(button_callback))

# Flask webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "BOT RUNNING"

if __name__ == "__main__":
    updater.bot.set_webhook(f"https://<your-render-url>.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
