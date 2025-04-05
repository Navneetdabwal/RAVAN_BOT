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

# /fake command
@bot.message_handler(commands=['fake'])
def fake_info(message):
    try:
        country = message.text.split()[1]
        r = requests.get(f"https://randomuser.me/api/?nat={country.lower()}")
        data = r.json()['results'][0]
        fake_data = f"""
*Fake Info ({country.upper()}):*
Name: {data['name']['first']} {data['name']['last']}
Address: {data['location']['street']['number']}, {data['location']['street']['name']}
City: {data['location']['city']}
State: {data['location']['state']}
Postcode: {data['location']['postcode']}
Phone: {data['phone']}
Email: {data['email']}
"""
        bot.reply_to(message, fake_data, parse_mode='Markdown')
    except:
        bot.reply_to(message, "Use like: /fake us")

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
