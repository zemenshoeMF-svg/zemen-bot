import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable robust logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION & LOCALIZATION ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Multilanguage dictionaries
TEXTS = {
    "en": {
        "welcome": (
            "🌟 *Welcome to Zemen Shoe Manufacturing PLC* 🌟\n\n"
            "Premier B2B Manufacturer of Custom Molded Rubber Soles in Addis Ababa, Ethiopia.\n"
            "Choose an option below to explore our high-performance industrial catalog, request custom tooling, "
            "or connect directly with our sales team."
        ),
        "btn_catalog": "📦 View Sole Catalog",
        "btn_custom": "🛠️ Custom Sole Inquiry",
        "btn_factory": "🏭 Factory & Quality",
        "btn_contact": "📞 Sales & Contact",
        "btn_lang": "🇪🇹 አማርኛ / English",
        "back": "⬅️ Back to Main Menu",
        "catalog_text": (
            "📦 *Zemen B2B Rubber Sole Catalog*\n\n"
            "Engineered for durability, maximum traction, and heavy-duty wear resistance.\n"
            "Select a product line below to view technical specifications and high-resolution visuals:"
        ),
        "product_1": "🥾 Heavy-Duty Work Boot Sole",
        "product_2": "👟 Premium Casual TR/Rubber Sole",
        "product_3": "🏃 Athletic & Trainer Sole Unit",
        "custom_text": (
            "🛠️ *Custom Molded Rubber Sole Development*\n\n"
            "We build custom molds tailored to your brand specifications. Provide your design brief, "
            "target volume, and durometer requirements by messaging our team directly."
        ),
        "factory_text": (
            "🏭 *Factory Excellence & Quality Control*\n\n"
            "Located in Addis Ababa, our production facility utilizes state-of-the-art vulcanization and "
            "precision molding machinery to supply top-tier footwear manufacturers across East Africa."
        ),
        "contact_text": (
            "📞 *Direct Corporate Communications*\n\n"
            "• *Location:* Addis Ababa, Ethiopia\n"
            "• *Email:* sales@zemenshoe.com\n"
            "• *Phone / Telegram:* +251 900 000 000\n"
            "• *Business Hours:* Mon - Sat (8:00 AM - 5:00 EAT)"
        ),
        "lang_switched": "language switched to English successfully.",
    },
    "am": {
        "welcome": (
            "🌟 *እንኳን ደህና መጡ ወደ ዘመን ጫማ ማምረቻ ኃ/የተ/የግ/ማህበር* 🌟\n\n"
            " በአዲስ አበባ፣ ኢትዮጵያ የሚገኝ ቀዳሚ የጎማ ሶል (Rubber Sole) አምራች ድርጅት።\n"
            "ከዚህ በታች ያሉትን አማራጮች በመጠቀም የምርት ካታሎጋችንን ይመልከቱ፣ የንግድ ጥያቄዎችን ያቅርቡ ወይም ከሽያጭ ቡድናችን ጋር ይገናኙ።"
        ),
        "btn_catalog": "📦 የሶል ካታሎግ ይመልከቱ",
        "btn_custom": "🛠️ ብጁ የሶል ማምረቻ ጥያቄ",
        "btn_factory": "🏭 የፋብሪካ መረጃ እና ጥራት",
        "btn_contact": "📞 የሽያጭ ማዕከል እና አድራሻ",
        "btn_lang": "🇬🇧 English / አማርኛ",
        "back": "⬅️ ወደ ዋናው ዝርዝር ይመለሱ",
        "catalog_text": (
            "📦 *የዘመን የጎማ ሶል ምርቶች*\n\n"
            "ለረጅም ጊዜ አገልግሎት፣ ለጠንካራ መያዣ (traction) እና ለከፍተኛ ጥራት የተነደፉ።\n"
            "ቴክኒካዊ መግለጫዎችን እና ምስሎችን ለማየት ከታች አንዱን ይምረጡ፦"
        ),
        "product_1": "🥾 የሥራ ቦት ጫማ ሶል (Work Boot)",
        "product_2": "👟 የዕለት ተዕለት ፕሪሚየም ሶል (Casual TR)",
        "product_3": "🏃 የስፖርት ጫማ ሶል (Athletic Unit)",
        "custom_text": (
            "🛠️ *ብጁ የጎማ ሶል ማምረቻ አገልግሎት*\n\n"
            "እንደ የምርት ስምዎ ፍላጎት ትክክለኛ ሞልዶችን እናዘጋጃለን። የንድፍ ሐሳብዎን እና የሚፈልጉትን መጠን በመላክ አብረውን ይስሩ።"
        ),
        "factory_text": (
            "🏭 *የፋብሪካችን የጥራት ደረጃ*\n\n"
            "በአዲስ አበባ የሚገኘው ማምረቻችን ዘመናዊ የሙቀት ማጣሪያ (vulcanization) እና የናሙና ማምረቻ ቴክኖሎጂዎችን ይጠቀማል።"
        ),
        "contact_text": (
            "📞 *የድርጅቱ አድራሻ እና የስልክ ቁጥሮች*\n\n"
            "• *አድራሻ፦* አዲስ አበባ፣ ኢትዮጵያ\n"
            "• *ኢሜይል፦* sales@zemenshoe.com\n"
            "• *ስልክ/ቴሌግራም፦* +251 900 000 000\n"
            "• *የሥራ ሰዓት፦* ከሰኞ እስከ ቅዳሜ (ከጠዋቱ 2:00 እስከ ማታ 11:00)"
        ),
        "lang_switched": "ቋንቋው ወደ አማርኛ ተቀይሯል።",
    },
}


def get_user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


def get_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    keyboard = [
        [InlineKeyboardButton(t["btn_catalog"], callback_data="menu_catalog")],
        [InlineKeyboardButton(t["btn_custom"], callback_data="menu_custom")],
        [
            InlineKeyboardButton(t["btn_factory"], callback_data="menu_factory"),
            InlineKeyboardButton(t["btn_contact"], callback_data="menu_contact"),
        ],
        [InlineKeyboardButton(t["btn_lang"], callback_data="toggle_lang")],
    ]
    return InlineKeyboardMarkup(keyboard)


# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(context)
    t = TEXTS[lang]
    keyboard = get_main_keyboard(lang)

    banner_url = "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80"

    if update.message:
        await update.message.reply_photo(
            photo=banner_url, caption=t["welcome"], reply_markup=keyboard, parse_mode="Markdown"
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=banner_url, caption=t["welcome"], parse_mode="Markdown"),
                reply_markup=keyboard,
            )
        except Exception:
            await query.edit_message_caption(caption=t["welcome"], reply_markup=keyboard, parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_user_lang(context)
    t = TEXTS[lang]

    back_btn = [[InlineKeyboardButton(t["back"], callback_data="main_menu")]]

    if data == "main_menu":
        await start(update, context)

    elif data == "toggle_lang":
        context.user_data["lang"] = "am" if lang == "en" else "en"
        new_lang = context.user_data["lang"]
        await query.answer(TEXTS[new_lang]["lang_switched"], show_alert=True)
        await start(update, context)

    elif data == "menu_catalog":
        keyboard = [
            [InlineKeyboardButton(t["product_1"], callback_data="prod_1")],
            [InlineKeyboardButton(t["product_2"], callback_data="prod_2")],
            [InlineKeyboardButton(t["product_3"], callback_data="prod_3")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")],
        ]
        await query.edit_message_caption(
            caption=t["catalog_text"], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    elif data in ["prod_1", "prod_2", "prod_3"]:
        prod_names = {
            "prod_1": ("Heavy-Duty Work Boot Sole", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80"),
            "prod_2": ("Premium Casual TR/Rubber Sole", "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800&auto=format&fit=crop&q=80"),
            "prod_3": ("Athletic & Trainer Sole Unit", "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800&auto=format&fit=crop&q=80"),
        }
        p_name, p_img = prod_names[data]
        caption = f"📦 *{p_name}*\n\n• High-grade durable rubber composite.\n• Excellent slip resistance.\n• Custom coloring & hardness available on bulk orders."
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Back to Catalog", callback_data="menu_catalog")],
            [InlineKeyboardButton(t["back"], callback_data="main_menu")],
        ]
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=p_img, caption=caption, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception:
            await query.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_custom":
        await query.edit_message_caption(
            caption=t["custom_text"], reply_markup=InlineKeyboardMarkup(back_btn), parse_mode="Markdown"
        )

    elif data == "menu_factory":
        await query.edit_message_caption(
            caption=t["factory_text"], reply_markup=InlineKeyboardMarkup(back_btn), parse_mode="Markdown"
        )

    elif data == "menu_contact":
        await query.edit_message_caption(
            caption=t["contact_text"], reply_markup=InlineKeyboardMarkup(back_btn), parse_mode="Markdown"
        )


async fn_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.warning("WARNING: Please set a valid TELEGRAM_BOT_TOKEN environment variable.")
        
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(fn_error)

    logger.info("Zemen Shoe Manufacturing Bot is starting up successfully...")
    app.run_polling()


if __name__ == "__main__":
    main()
