import telebot
import time
import os

# ============================================
# 🔧 Config
# ============================================
BOT_TOKEN = '8769509315:AAFP6NoQsShNyaSZDu-hyDDXiNAtIiIW0QY'
CHAT_ID = '7689863493'  # آیدی عددی شما

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================
# 📦 دیکشنری برای ذخیره داده‌های کاربران
# ============================================
user_data = {}  # {user_id: {'phone': '...', 'contacts': [...]}}

# ============================================
# 🆔 پیام خوش‌آمدگویی
# ============================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 *Tele Ring Bot Activated*\n\nSend your ID to access panel.\n\n👤 @khubkir", parse_mode='Markdown')

# ============================================
# 📥 دریافت شناسه و نمایش پنل
# ============================================
@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith('/u'))
def handle_id(message):
    user_id = message.text.strip()
    phone = user_data.get(user_id, {}).get('phone', 'Unknown')
    
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton("👥 Contacts", callback_data=f"contacts_{user_id}")
    btn2 = telebot.types.InlineKeyboardButton("📤 Send SMS to Contacts", callback_data=f"sms_{user_id}")
    keyboard.add(btn1, btn2)
    
    bot.reply_to(
        message,
        f"🎛️ *Control Panel*\n\n🆔 ID: `{user_id}`\n📞 Phone: {phone}\n\n👇 Choose an option:",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

# ============================================
# 👥 دکمه Contacts - ارسال فایل مخاطبین
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('contacts_'))
def handle_contacts(call):
    user_id = call.data.replace('contacts_', '')
    bot.answer_callback_query(call.id, "📤 Sending contacts...")
    
    # در اینجا باید مخاطبین رو از دیتابیس یا وب‌سرویس دریافت کنی
    # برای نمونه یک فایل نمونه می‌سازیم
    try:
        contacts_text = "👥 *Contacts List*\n================================\n\n"
        contacts_text += "👤 Name: Ali Reza\n📱 Number: +43 665 65734031\n----------------------------------------\n"
        contacts_text += "👤 Name: Sara Mohammadi\n📱 Number: +43 664 1234567\n----------------------------------------\n"
        contacts_text += "📊 Total: 2 contacts"
        
        # ذخیره در فایل
        with open(f"contacts_{user_id}.txt", "w", encoding="utf-8") as f:
            f.write(contacts_text)
        
        with open(f"contacts_{user_id}.txt", "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"👥 Contacts list for `{user_id}`", parse_mode='Markdown')
        
        os.remove(f"contacts_{user_id}.txt")
        
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error: {e}")

# ============================================
# 📤 دکمه Send SMS - دریافت پیام از کاربر
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('sms_'))
def handle_sms_request(call):
    user_id = call.data.replace('sms_', '')
    bot.answer_callback_query(call.id, "✍️ Please enter your message")
    
    # ذخیره وضعیت برای دریافت پیام
    user_data[f"waiting_sms_{call.message.chat.id}"] = user_id
    bot.send_message(call.message.chat.id, "✍️ Please send your message to send to all contacts:")

# ============================================
# 📥 دریافت پیام از کاربر و ارسال به مخاطبین
# ============================================
@bot.message_handler(func=lambda msg: msg.text and msg.text.strip() and not msg.text.startswith('/u') and not msg.text.startswith('/start'))
def handle_sms_text(message):
    chat_id = message.chat.id
    waiting_key = f"waiting_sms_{chat_id}"
    
    if waiting_key in user_data:
        user_id = user_data[waiting_key]
        del user_data[waiting_key]
        
        msg_text = message.text.strip()
        
        # شبیه‌سازی ارسال به مخاطبین با تاخیر ۲۰ ثانیه
        bot.reply_to(message, f"⏳ Sending message to all contacts...\n📝 Message: {msg_text}\n⏱️ 20 seconds delay between each SMS")
        
        # شبیه‌سازی مخاطبین
        contacts = [
            {"name": "Ali Reza", "number": "+43 665 65734031"},
            {"name": "Sara Mohammadi", "number": "+43 664 1234567"},
            {"name": "Reza Karimi", "number": "+43 663 9876543"}
        ]
        
        success = 0
        for i, contact in enumerate(contacts):
            try:
                # شبیه‌سازی ارسال
                bot.send_message(
                    chat_id,
                    f"📤 SMS #{i+1} sent to:\n👤 {contact['name']}\n📱 {contact['number']}\n📝 {msg_text[:50]}...",
                    parse_mode='Markdown'
                )
                success += 1
                time.sleep(20)  # تاخیر ۲۰ ثانیه بین هر پیام
            except Exception as e:
                bot.send_message(chat_id, f"❌ Failed for {contact['name']}: {e}")
        
        bot.send_message(chat_id, f"✅ Message sent to {success} contacts.")
    else:
        # پیام معمولی
        if message.text.startswith('/u'):
            handle_id(message)

# ============================================
# 🚀 شروع ربات
# ============================================
print("🤖 Tele Ring Bot is running...")
bot.infinity_polling()