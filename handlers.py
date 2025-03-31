# handlers.py

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext
from config import ADMIN_ID, REGISTER_URL
from database import save_user_data, get_user_count, get_all_users_short
from states import ASK_NAME, ASK_AGE, ASK_EDUCATION, ASK_REASON, WAITING_FOR_SCREENSHOT

# شروع ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎓 خوش اومدی به دوره رایگان آموزش تعمیرات موبایل!\n"
        "اگه واقعاً می‌خوای وارد این مسیر بشی، چندتا سوال ساده ازت می‌پرسم.\n\n"
        "لطفاً نام و نام خانوادگی خودتو وارد کن:"
    )
    return ASK_NAME

# دریافت نام
def ask_name(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text
    update.message.reply_text("سن شما چند ساله است؟")
    return ASK_AGE

# دریافت سن
def ask_age(update: Update, context: CallbackContext):
    context.user_data['age'] = update.message.text
    update.message.reply_text("مدرک تحصیلی‌ات چیه؟")
    return ASK_EDUCATION

# دریافت مدرک تحصیلی
def ask_education(update: Update, context: CallbackContext):
    context.user_data['education'] = update.message.text
    update.message.reply_text("چی باعث شده بخوای وارد این دوره بشی؟")
    return ASK_REASON

# دریافت انگیزه
def ask_reason(update: Update, context: CallbackContext):
    context.user_data['reason'] = update.message.text
    # ذخیره اطلاعات کاربر
    save_user_data(
        context.user_data['name'],
        context.user_data['age'],
        context.user_data['education'],
        context.user_data['reason']
    )

    update.message.reply_text(
        f"🔗 خیلی عالی! حالا برای ورود به دوره، لطفاً از طریق لینک زیر ثبت‌نام کن:\n{REGISTER_URL}\n\n"
        "📸 بعد از ثبت‌نام، لطفاً یه اسکرین‌شات از ثبت‌نامت برام بفرست تا بررسی بشه."
    )
    return WAITING_FOR_SCREENSHOT

# دریافت اسکرین‌شات
def receive_screenshot(update: Update, context: CallbackContext):
    update.message.reply_text(
        "✅ اسکرین‌شات دریافت شد.\n"
        "🔒 لطفاً منتظر باش تا بررسی بشه و لینک کانال VIP برات ارسال بشه."
    )
    return ConversationHandler.END

# دکمه فقط برای ادمین: نمایش آمار ثبت‌نام
def show_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ شما به این بخش دسترسی ندارید.")
        return

    count = get_user_count()
    users = get_all_users_short()
    response = f"📊 تعداد ثبت‌نام‌ها: {count}\n\n"
    response += "\n".join(users) if users else "هیچ ثبت‌نامی ثبت نشده."
    update.message.reply_text(response)

# خروج از گفت‌وگو
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ گفتگو لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
