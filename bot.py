
import os
import random
import string
import requests
from flask import Flask, request
import telebot

API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

def generate_cc(bin_input, amount=15):
    result = []
    while len(result) < amount:
        cc = bin_input
        while len(cc) < 16:
            cc += str(random.randint(0, 9))
        mm = str(random.randint(1, 12)).zfill(2)
        yy = str(random.randint(25, 30))
        cvv = str(random.randint(100, 999))
        result.append(f"{cc}|{mm}|{yy}|{cvv}")
    return result

def get_bin_info(bin_number):
    try:
        res = requests.get(f"https://lookup.binlist.net/{bin_number}")
        if res.status_code == 200:
            data = res.json()
            info = f"""
Valid BIN: Yes
Scheme: {data.get('scheme', 'N/A')}
Type: {data.get('type', 'N/A')}
Brand: {data.get('brand', 'N/A')}
Bank: {data['bank']['name'] if 'bank' in data else 'N/A'}
Country: {data['country']['name'] if 'country' in data else 'N/A'}
"""
            return info
        else:
            return "Invalid BIN or not found!"
    except:
        return "Error checking BIN!"

def get_fake_address(country):
    try:
        res = requests.get(f"https://randomuser.me/api/?nat={country[:2].lower()}")
        if res.status_code == 200:
            d = res.json()['results'][0]
            return f"{d['name']['first']} {d['name']['last']}, {d['location']['street']['number']} {d['location']['street']['name']}, {d['location']['city']}, {d['location']['state']}, {d['location']['country']} - {d['location']['postcode']}"
        else:
            return "Couldn't fetch fake address!"
    except:
        return "Error generating address!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = (
        "Welcome to RAVAN_BOT!\n"
        "Created by ⇝ 『𝙉𝘼𝙑𝙉𝙀𝙀𝙏 𝘿𝘼𝘽𝙒𝘼𝙇』\n\n"
        "Available Commands:\n"
        "/gen <bin> - Generate 15 CCs\n"
        "/gnt <bin> - Same as /gen\n"
        "/chk <cc> - Check if CC is live\n"
        "/mass - Check multiple CCs (paste list)\n"
        "/bin <bin> - BIN info & validation\n"
        "/vbv <bin> - VBV status (Mock)\n"
        "/fake <country> - Fake address\n"
        "/help - Show help"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['gen', 'gnt'])
def handle_gen(message):
    try:
        bin_input = message.text.split()[1]
        if len(bin_input) < 6:
            bot.reply_to(message, "BIN must be at least 6 digits.")
            return
        cards = generate_cc(bin_input)
        bot.reply_to(message, "\n".join(cards))
    except:
        bot.reply_to(message, "Usage: /gen 123456")

@bot.message_handler(commands=['bin'])
def handle_bin(message):
    try:
        bin_number = message.text.split()[1]
        info = get_bin_info(bin_number)
        bot.reply_to(message, info)
    except:
        bot.reply_to(message, "Usage: /bin <bin>")

@bot.message_handler(commands=['vbv'])
def handle_vbv(message):
    try:
        bin_number = message.text.split()[1]
        mock = "VBV" if int(bin_number[-1]) % 2 == 0 else "NON-VBV"
        bot.reply_to(message, f"{bin_number} is {mock}")
    except:
        bot.reply_to(message, "Usage: /vbv <bin>")

@bot.message_handler(commands=['fake'])
def handle_fake(message):
    try:
        country = message.text.split()[1]
        address = get_fake_address(country)
        bot.reply_to(message, address)
    except:
        bot.reply_to(message, "Usage: /fake <country>")

@bot.message_handler(commands=['chk'])
def handle_chk(message):
    cc = message.text.split()[1]
    bot.reply_to(message, f"Card {cc} is Live (Mock Result)")

@bot.message_handler(commands=['mass'])
def handle_mass(message):
    try:
        ccs = message.reply_to_message.text.splitlines()
        result = ""
        for c in ccs[:15]:
            result += f"{c} => Live (Mock)\n"
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "Reply to a message containing CC list with /mass")

@app.route(f"/{API_TOKEN}", methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def home():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://<your-render-url>.onrender.com/{API_TOKEN}")
    return "Webhook set", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
        
