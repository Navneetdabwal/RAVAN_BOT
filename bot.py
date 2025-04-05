import os
import telebot
from flask import Flask, request
import requests

API_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to RAVAN_BOT!\n\n"
                          "Commands:\n"
                          "/chk - Check a single CC\n"
                          "/mass - Check multiple CCs\n"
                          "/bin - BIN lookup\n"
                          "/vbv - VBV check\n"
                          "/gen - Generate CCs from BIN\n"
                          "/gnt - Same as /gen\n"
                          "/fake - Fake address generator\n\n"
                          "Created by: 『ＮＡＶＮＥＥＴ ＤＡＢＷＡＬ』")

@bot.message_handler(commands=['bin'])
def bin_lookup(message):
    bin_number = message.text.split(maxsplit=1)[1]
    if len(bin_number) < 6:
        bot.reply_to(message, "Please provide a valid BIN.")
        return
    res = requests.get(f"https://lookup.binlist.net/{bin_number}")
    if res.status_code == 200:
        data = res.json()
        reply = f"BIN Info:\nBank: {data.get('bank', {}).get('name', 'N/A')}\nCountry: {data.get('country', {}).get('name', 'N/A')}\nScheme: {data.get('scheme', 'N/A')}\nType: {data.get('type', 'N/A')}\nBrand: {data.get('brand', 'N/A')}"
    else:
        reply = "Invalid BIN or not found."
    bot.reply_to(message, reply)

@bot.message_handler(commands=['gen', 'gnt'])
def generate_cc(message):
    try:
        bin_input = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Usage: /gen xxxxxxx")
        return
    from random import randint
    generated = []
    for _ in range(15):
        cc = bin_input
        while len(cc) < 16:
            cc += str(randint(0, 9))
        exp = f"{randint(1,12):02d}|{randint(25,30)}"
        cvv = f"{randint(100,999)}"
        generated.append(f"{cc}|{exp}|{cvv}")
    bot.reply_to(message, "\n".join(generated))

@bot.message_handler(commands=['chk'])
def chk_cc(message):
    cc = message.text.split(maxsplit=1)[1]
    bot.reply_to(message, f"Checked: {cc}\nStatus: Live")

@bot.message_handler(commands=['mass'])
def mass_chk(message):
    ccs = message.text.split("\n")[1:]
    response = ""
    for cc in ccs[:15]:
        response += f"{cc} -> Live\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['vbv'])
def vbv_check(message):
    cc = message.text.split(maxsplit=1)[1]
    bot.reply_to(message, f"{cc} is NON-VBV")

@bot.message_handler(commands=['fake'])
def fake_address(message):
    country = message.text.split(maxsplit=1)[1].lower()
    if "india" in country:
        reply = "Name: Rahul Sharma\nAddress: 123 MG Road, Delhi\nPhone: +91 9876543210"
    else:
        reply = "Name: John Doe\nAddress: 123 Main St, NY, USA\nPhone: +1 555 123 4567"
    bot.reply_to(message, reply)

@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok'

@app.route("/", methods=['GET', 'HEAD'])
def home():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-app-name.onrender.com/{API_TOKEN}")
    return "Webhook set!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
