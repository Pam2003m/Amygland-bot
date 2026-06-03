"""
ربات تلگرام آمیگلند
نیازمندی‌ها:
    pip install python-telegram-bot==20.7
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ─── تنظیمات ───────────────────────────────────────────────────────────────
BOT_TOKEN = "8833146675:AAF_CskdgUsPSxM2fG3AgpJS3La2YJz7a-U"
ADMIN_CHAT_ID = "YOUR_GROUP_OR_CHANNEL_ID"
# ───────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# مراحل مکالمه
(
    MAIN_MENU,
    ANONYMOUS_MSG,
    FULL_NAME,
    PHONE,
    FIELD,
    PROVINCE,
    CITY,
    SCHOOL,
    GRADE,
    HAS_ADVISOR,
    EXPECTATIONS,
    MAIN_PROBLEM,
    PLAN,
    CONFIRM,
) = range(14)

FIELDS = ["ریاضی", "تجربی", "انسانی"]
GRADES = ["دهم", "یازدهم", "دوازدهم", "فارغ‌التحصیل"]
YES_NO = ["بله", "خیر"]

PLANS = {
    "طرح نهایی مستر 🚀":       "تا انتهای امتحانات نهایی — ۱,۵۰۰,۰۰۰ تومان",
    "طرح فینیشر 🏁":            "نهایی و کنکور — ۱,۵۰۰,۰۰۰ تومان/ماه",
    "طرح آمادگی فرهنگیان 🎓":  "تا انتهای مصاحبه — ۲,۵۰۰,۰۰۰ تومان",
    "طرح الماس 💎 VIP":         "کنکوری ۱۴۰۶ به بعد — ۱,۸۰۰,۰۰۰ تومان/ماه",
    "طرح طلایی 🥇":             "کنکوری ۱۴۰۶ به بعد — ۱,۴۵۰,۰۰۰ تومان",
    "طرح نقره‌ای 🥈":           "کنکوری ۱۴۰۶ به بعد — ۱,۱۰۰,۰۰۰ تومان",
    "طرح برنز 🥉":              "کنکوری ۱۴۰۶ به بعد — ۸۵۰,۰۰۰ تومان",
}
PLAN_NAMES = list(PLANS.keys())


# ─── منوی اصلی ─────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    keyboard = [["📩 ارسال پیام ناشناس", "📋 رزرو مشاوره"]]
    await update.message.reply_text(
        "به مشاوره کنکور و نهایی آمیگلند 🧠 خوش اومدی !\n"
        "اینجا هستیم تا توی هر مشکلی برات راه حل باشیم❤️\n\n"
        "یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip()

    if choice == "📩 ارسال پیام ناشناس":
        await update.message.reply_text(
            "🔒 *پیام ناشناس*\n\n"
            "سوالت رو بنویس، بدون اینکه کسی بفهمه کی هستی برای آمیگلند ارسال می‌شه👇",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ANONYMOUS_MSG

    elif choice == "📋 رزرو مشاوره":
        await update.message.reply_text(
            "✅ عالیه! بریم ثبت‌نام رو شروع کنیم.\n\n"
            "لطفاً *نام و نام خانوادگی* کاملت رو بنویس:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FULL_NAME

    else:
        keyboard = [["📩 ارسال پیام ناشناس", "📋 رزرو مشاوره"]]
        await update.message.reply_text(
            "❗ لطفاً یکی از گزینه‌ها رو انتخاب کن:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return MAIN_MENU


# ─── پیام ناشناس ───────────────────────────────────────────────────────────
async def anonymous_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text.strip()
    user = update.effective_user

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "📩 *پیام ناشناس جدید*\n"
                "━━━━━━━━━━━━━━━━━\n"
                f"{msg}"
            ),
            parse_mode="Markdown",
        )
        await update.message.reply_text(
            "✅ پیامت ارسال شد!\n\n"
            "آمیگلند هرچی سریعتر بهت جواب میده 😊\n\n"
            "برای بازگشت به منو /start بزن.",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        logger.error(f"Error sending anonymous message: {e}")
        await update.message.reply_text(
            "❌ مشکلی پیش اومد. دوباره تلاش کن.",
            reply_markup=ReplyKeyboardRemove(),
        )

    return ConversationHandler.END


# ─── ثبت‌نام مشاوره ────────────────────────────────────────────────────────
async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text("❗ لطفاً نام کامل خود را وارد کنید.")
        return FULL_NAME
    context.user_data["full_name"] = name
    await update.message.reply_text(
        f"✅ ممنون {name}!\n\n📱 حالا *شماره موبایل* خودت رو وارد کن:",
        parse_mode="Markdown",
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text.strip().replace(" ", "").replace("-", "")
    if not (phone.startswith("09") and len(phone) == 11 and phone.isdigit()):
        await update.message.reply_text("❗ شماره موبایل معتبر نیست.\nمثال: 09123456789")
        return PHONE
    context.user_data["phone"] = phone
    keyboard = [[f] for f in FIELDS]
    await update.message.reply_text(
        "📚 *رشته کنکور* خودت رو انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return FIELD


async def get_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    field = update.message.text.strip()
    if field not in FIELDS:
        await update.message.reply_text("❗ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
        return FIELD
    context.user_data["field"] = field
    await update.message.reply_text(
        "🗺️ *استان* محل سکونتت رو بنویس:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PROVINCE


async def get_province(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["province"] = update.message.text.strip()
    await update.message.reply_text("🏙️ *شهر* محل سکونتت رو بنویس:", parse_mode="Markdown")
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text("🏫 *نام مدرسه‌ات* رو بنویس:", parse_mode="Markdown")
    return SCHOOL


async def get_school(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["school"] = update.message.text.strip()
    keyboard = [[g] for g in GRADES]
    await update.message.reply_text(
        "📖 *پایه تحصیلی* فعلیت رو انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GRADE


async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    grade = update.message.text.strip()
    if grade not in GRADES:
        await update.message.reply_text("❗ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
        return GRADE
    context.user_data["grade"] = grade
    keyboard = [[y] for y in YES_NO]
    await update.message.reply_text(
        "🧑‍💼 آیا قبلاً *مشاور تحصیلی* داشتی؟",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return HAS_ADVISOR


async def get_has_advisor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ans = update.message.text.strip()
    if ans not in YES_NO:
        await update.message.reply_text("❗ لطفاً بله یا خیر انتخاب کن.")
        return HAS_ADVISOR
    context.user_data["has_advisor"] = ans
    await update.message.reply_text(
        "💬 *انتظاراتت از مشاور* چیه؟ (چند جمله بنویس)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return EXPECTATIONS


async def get_expectations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["expectations"] = update.message.text.strip()
    await update.message.reply_text("⚠️ *بزرگ‌ترین مشکل درسیت* چیه؟", parse_mode="Markdown")
    return MAIN_PROBLEM


async def get_main_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["main_problem"] = update.message.text.strip()
    plan_list = "\n".join([f"• *{name}*: {desc}" for name, desc in PLANS.items()])
    keyboard = [[name] for name in PLAN_NAMES]
    await update.message.reply_text(
        f"💼 *انتخاب طرح مشاوره:*\n\n{plan_list}\n\nکدوم طرح رو انتخاب می‌کنی؟",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return PLAN


async def get_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    plan = update.message.text.strip()
    if plan not in PLAN_NAMES:
        await update.message.reply_text("❗ لطفاً یکی از طرح‌های موجود را انتخاب کنید.")
        return PLAN
    context.user_data["plan"] = f"{plan} ({PLANS[plan]})"

    d = context.user_data
    summary = (
        "📋 *خلاصه اطلاعات ثبت‌نام:*\n\n"
        f"👤 نام: {d['full_name']}\n"
        f"📱 شماره: {d['phone']}\n"
        f"📚 رشته: {d['field']}\n"
        f"🗺️ استان: {d['province']}\n"
        f"🏙️ شهر: {d['city']}\n"
        f"🏫 مدرسه: {d['school']}\n"
        f"📖 پایه: {d['grade']}\n"
        f"🧑‍💼 سابقه مشاور: {d['has_advisor']}\n"
        f"💬 انتظارات: {d['expectations']}\n"
        f"⚠️ مشکل اصلی: {d['main_problem']}\n"
        f"💼 طرح انتخابی: {d['plan']}\n\n"
        "✅ آیا اطلاعات صحیح است؟"
    )
    keyboard = [["✅ تأیید و ارسال", "❌ شروع مجدد"]]
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip()

    if choice == "❌ شروع مجدد":
        return await start(update, context)

    if choice != "✅ تأیید و ارسال":
        await update.message.reply_text("❗ لطفاً یکی از گزینه‌ها را انتخاب کنید.")
        return CONFIRM

    d = context.user_data
    user = update.effective_user
    telegram_info = f"@{user.username}" if user.username else f"ID: {user.id}"

    message = (
        "🆕 *ثبت‌نام جدید کنکوری*\n"
        "━━━━━━━━━━━━━━━━━\n"
        f"👤 *نام:* {d['full_name']}\n"
        f"📱 *شماره:* `{d['phone']}`\n"
        f"📚 *رشته:* {d['field']}\n"
        f"🗺️ *استان:* {d['province']}\n"
        f"🏙️ *شهر:* {d['city']}\n"
        f"🏫 *مدرسه:* {d['school']}\n"
        f"📖 *پایه:* {d['grade']}\n"
        f"🧑‍💼 *سابقه مشاور:* {d['has_advisor']}\n"
        f"💬 *انتظارات:* {d['expectations']}\n"
        f"⚠️ *مشکل اصلی:* {d['main_problem']}\n"
        f"💼 *طرح انتخابی:* {d['plan']}\n"
        "━━━━━━━━━━━━━━━━━\n"
        f"🔗 *تلگرام:* {telegram_info}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="Markdown")
        await update.message.reply_text(
            "🎉 *ثبت‌نامت با موفقیت انجام شد!*\n\n"
            "✅ اطلاعاتت ثبت شد و تیم مشاوران ما در اسرع وقت با شماره‌ای که وارد کردی باهات تماس می‌گیرن. 📞\n\n"
            "موفق باشی در کنکور! 🌟",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        logger.error(f"Error sending to admin: {e}")
        await update.message.reply_text(
            "❌ مشکلی پیش اومد. لطفاً دوباره تلاش کن یا با پشتیبانی تماس بگیر.",
            reply_markup=ReplyKeyboardRemove(),
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ لغو شد.\nهر وقت خواستی /start بزن.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای شروع /start بزن.")


# ─── اجرا ──────────────────────────────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU:    [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            ANONYMOUS_MSG:[MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_msg)],
            FULL_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            FIELD:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_field)],
            PROVINCE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_province)],
            CITY:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            SCHOOL:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_school)],
            GRADE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_grade)],
            HAS_ADVISOR:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_has_advisor)],
            EXPECTATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_expectations)],
            MAIN_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_main_problem)],
            PLAN:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_plan)],
            CONFIRM:      [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("ربات در حال اجراست...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
