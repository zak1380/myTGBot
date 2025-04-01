import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, ADMIN_ID, REGISTER_URL
from database import save_user_data, get_all_user_ids



from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()











bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}
waiting_users = {}
screenshot_messages = {}  # key = msg_id, value = user_id

broadcast_mode = False  # وضعیت انتظار متن ادمین

# /start
@bot.message_handler(commands=['start'])
def start(message: Message):
    chat_id = message.chat.id

    if message.from_user.id == ADMIN_ID:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            KeyboardButton("📊 مشاهده آمار ثبت‌نام"),
            KeyboardButton("📣 یادآوری به ثبت‌نام‌نشده‌ها"),
            KeyboardButton("📤 ارسال پیام به همه")
        )
        bot.send_message(chat_id, "به پنل مدیریت خوش آمدید.", reply_markup=markup)
        return

    bot.send_message(chat_id,
        "🎓 خوش اومدی به دوره رایگان آموزش تعمیرات موبایل!\n\n"
        "لطفاً نام و نام خانوادگی خودت رو وارد کن:")
    user_states[chat_id] = {'step': 'ask_name'}

# پیام‌های متنی
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_messages(message: Message):
    global broadcast_mode
    chat_id = message.chat.id
    text = message.text

    # مدیریت پنل ادمین
    if message.from_user.id == ADMIN_ID:
        if broadcast_mode:
            user_ids = get_all_user_ids()
            sent_count = 0
            for uid in user_ids:
                try:
                    bot.send_message(int(uid), f"📢 پیام ادمین:\n{text}")
                    sent_count += 1
                except:
                    pass
            bot.send_message(chat_id, f"✅ پیام برای {sent_count} نفر ارسال شد.")
            broadcast_mode = False
            return

        if text == "📊 مشاهده آمار ثبت‌نام":
            user_ids = get_all_user_ids()
            count = len(set(user_ids))
            ids_text = "\n".join([f"- {uid}" for uid in set(user_ids)])
            bot.send_message(chat_id,
                f"📊 تعداد ثبت‌نام‌های یونیک تا این لحظه: {count}\n\n🆔 لیست آیدی‌ها:\n{ids_text}")
            return

        elif text == "📣 یادآوری به ثبت‌نام‌نشده‌ها":
            for uid in waiting_users.keys():
                try:
                    bot.send_message(uid,
                                     "🚀 دوست عزیز!\n\n"
                                     "تا این لحظه 89 نفر با ثبت‌نام در دوره، دارن آینده شغلی‌شون رو می‌سازن 👷‍♂️📱\n"
                                     "تو فقط یه اسکرین‌شات با ما فاصله داری!\n\n"
                                     "📌 از این لینک ثبت‌نام کن و عکسشو بفرست:\n"
                                     "🔗 https://my.tlyn.ir/register?referral=AQMVWER\n\n"
                                     "📸 بعد از ارسال اسکرین‌شات، وارد کانال VIP می‌شی 💎\n"
                                     "⏳ فرصت رو از دست نده! فقط تا فردا فرصت داری")

                except:
                    pass
            bot.send_message(chat_id, f"📬 پیام یادآوری برای {len(waiting_users)} نفر ارسال شد.")
            return

        elif text == "📤 ارسال پیام به همه":
            broadcast_mode = True
            bot.send_message(chat_id, "📝 لطفاً پیام خود را بنویسید تا برای همه ارسال شود:")
            return

    if chat_id not in user_states:
        return

    state = user_states[chat_id]

    if state['step'] == 'ask_name':
        state['name'] = text
        state['step'] = 'ask_age'
        bot.send_message(chat_id, "📌 چند سالته؟")

    elif state['step'] == 'ask_age':
        state['age'] = text
        state['step'] = 'ask_education'
        bot.send_message(chat_id, "🎓 مدرک تحصیلی شما چیه؟")

    elif state['step'] == 'ask_education':
        state['education'] = text
        state['step'] = 'ask_experience'
        bot.send_message(chat_id, "📱 آیا قبلاً تجربه‌ای در زمینه تعمیر یا کار با موبایل داشتی؟")

    elif state['step'] == 'ask_experience':
        state['experience'] = text
        state['step'] = 'ask_interest'
        bot.send_message(chat_id, "🔧 به کدوم بخش علاقه‌مندتری؟ (نرم‌افزار، سخت‌افزار، یا هر دو؟)")

    elif state['step'] == 'ask_interest':
        state['interest'] = text
        state['step'] = 'ask_reason'
        bot.send_message(chat_id, "💬 چرا می‌خوای تو این دوره شرکت کنی؟ انگیزه‌ت چیه؟")

    elif state['step'] == 'ask_reason':
        state['reason'] = text
        save_user_data(chat_id, state['name'], state['age'], state['education'],
                       state['experience'], state['interest'], state['reason'])

        info = (
            f"📥 ثبت‌نام جدید:\n\n"
            f"👤 نام: {state['name']}\n"
            f"🎂 سن: {state['age']}\n"
            f"🎓 مدرک: {state['education']}\n"
            f"📱 تجربه قبلی: {state['experience']}\n"
            f"🔧 علاقه: {state['interest']}\n"
            f"💬 انگیزه: {state['reason']}\n"
            f"🆔 @{message.from_user.username or 'ندارد'}\n"
            f"👤 chat_id: {chat_id}"
        )
        bot.send_message(ADMIN_ID, info)

        waiting_users[chat_id] = True

        bot.send_message(chat_id,
            "✅ ثبت شد!\n\n"
            "🔔 حالا یه مرحله ساده مونده!\n\n"
            "💡 ما این دوره رو با زحمت زیادی رایگان کردیم. اما برای اینکه بتونیم همین روند رو ادامه بدیم و هزینه‌ها تأمین بشه، فقط یه کاری ازت می‌خوایم:\n\n"
            "📌 لطفاً توی سایت معتبر **طلاین (Tlyan.ir)** ثبت‌نام کن.\n"
            "🏆 با ثبت‌نام، ۷ سوت طلا هم برای تو و هم برای من میاد 💰\n"
            f"🔗 لینک ثبت‌نام: {REGISTER_URL}\n\n"
            "📸 بعد از ثبت‌نام، فقط یه اسکرین‌شات بفرست تا تأییدت کنیم.\n"
            "✅ بعدش لینک کانال VIP برات ارسال میشه.\n\n"
            "مرسی که همراه مایی ❤️"
        )

        state['step'] = 'waiting_for_screenshot'

    elif state['step'] == 'waiting_for_screenshot':
        bot.send_message(chat_id, "📸 لطفاً فقط اسکرین‌شات ثبت‌نام رو ارسال کن تا بتونیم تأییدت کنیم.")

# عکس یا فایل (اسکرین‌شات)
@bot.message_handler(content_types=['photo', 'document'])
def handle_screenshot(message: Message):
    chat_id = message.chat.id
    if chat_id not in user_states:
        return

    state = user_states[chat_id]
    if state.get('step') == 'waiting_for_screenshot':
        # فوروارد واقعی تا forward_from کار کنه
        bot.forward_message(ADMIN_ID, chat_id, message.message_id)

        bot.send_message(chat_id, "📸 اسکرین‌شات دریافت شد!\n⏳ لطفاً منتظر تأیید ادمین باش.\n📬 پس از تأیید، لینک ورود به کانال برات ارسال میشه.")
        user_states.pop(chat_id)
        waiting_users.pop(chat_id, None)



@bot.message_handler(func=lambda msg: msg.reply_to_message and msg.from_user.id == ADMIN_ID)
def reply_to_screenshot(message: Message):
    try:
        forwarded = message.reply_to_message
        if not forwarded.forward_from:
            bot.send_message(ADMIN_ID, "❗ این پیام فوروارد‌شده نیست. لطفاً روی پیام فورواردشده‌ی اسکرین‌شات ریپلای کن.")
            return

        target_user_id = forwarded.forward_from.id
        bot.send_message(target_user_id, f"📩 پیام ادمین:\n{message.text}")
        bot.send_message(ADMIN_ID, "✅ پیام با موفقیت برای کاربر ارسال شد.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ خطا در ارسال پیام: {e}")













# ادمین با ریپلای به پیام عکس (اسکرین‌شات) پیام بده به کاربر


# دستور /send برای پیام مستقیم
@bot.message_handler(commands=['send'])
def send_to_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split(" ", 2)
        user_id = int(args[1])
        text = args[2]
        bot.send_message(user_id, f"📩 پیام ادمین:\n{text}")
        bot.send_message(ADMIN_ID, "✅ پیام با موفقیت ارسال شد.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ خطا در ارسال پیام: {e}")



print("🤖 Bot is running...")
bot.polling()
