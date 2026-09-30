import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Enable robust logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION & LOCALIZATION ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Refined bilingual dictionaries using preferred industry terminology
TEXTS = {
    "en": {
        "welcome": (
            "🌟 *Zemen Shoe Manufacturing PLC* 🌟\n\n"
            "Addis Ababa's premier B2B manufacturer specializing in high-performance molded rubber soles and industrial shoe components.\n\n"
            "Select an option below to browse our catalog, discuss custom mold development, or connect with our sales team."
        ),
        "btn_catalog": "📦 View Sole Catalog",
        "btn_custom": "🛠️ Custom Sole Inquiry",
        "btn_factory": "🏭 Factory & Quality Standards",
        "btn_contact": "📞 Sales & Direct Contact",
        "btn_lang": "🇪🇹 አማርኛ / English",
        "back": "⬅️ Back to Main Menu",
        "catalog_text": (
            "📦 *Industrial Rubber Sole Catalog*\n\n"
            "Engineered for exceptional durability, slip resistance, and heavy-duty wear. "
            "Choose a product line below to view technical specifications and visual details:"
        ),
        "product_1": "🥾 Heavy-Duty Work Boot Sole",
        "product_2": "👟 Casual TR & Rubber Sole Unit",
        "product_3": "🏃 Athletic & Trainer Sole Unit",
        "custom_text": (
            "🛠️ *Custom Mold Development*\n\n"
            "We design and manufacture bespoke rubber molds tailored to your exact brand specifications. "
            "Send your design brief, target volume, and technical requirements straight to our engineering team."
        ),
        "factory_text": (
            "🏭 *Factory & Quality Assurance*\n\n"
            "Operating from our advanced production facility in Addis Ababa, we utilize precision vulcanization "
            "machinery and strict quality controls to supply leading footwear brands across the region."
        ),
        "contact_text": (
            "📞 *Corporate Sales Office*\n\n"
            "• *Location:* Addis Ababa, Ethiopia\n"
            "• *Email:* sales@zemenshoe.com\n"
            "• *Phone / Telegram:* +251 900 000 000\n"
            "• *Working Hours:* Monday – Saturday (2:00 Local - 11:00 Local)"
        ),
        "lang_switched": "Switched to English.",
    },
    "am": {
        "welcome": (
            "🌟 *ዘመን ጫማ ማምረቻ ኃ/የተ/የግ/ማህበር* 🌟\n\n"
            "በአዲስ አበባ ከተማ የሚገኝ ቀዳሚ የኢንዱስትሪ የጎማ ሶል (Rubber Sole) እና የጫማ ዕቃዎች አምራች ድርጅት።\n\n"
            "የምርት ካታሎጋችንን ለመመልከት፣ Custom (ብጁ) ሞልድ ማምረቻ ጥያቄ ለማቅረብ ወይም ከሽያጭ ቡድናችን ጋር ለመነጋገር ከታች ያሉትን አማራጮች ይጠቀሙ።"
        ),
        "btn_catalog": "📦 የሶል ካታሎግ ይመልከቱ",
        "btn_custom": "🛠️ Custom Sole Inquiry",
        "btn_factory": "🏭 ፋብሪካችን እና የጥራት ደረጃ",
        "btn_contact": "📞 የሽያጭ ማዕከል አድራሻ",
        "btn_lang": "🇬🇧 English / አማርኛ",
        "back": "⬅️ ወደ ዋናው ዝርዝር ተመለስ",
        "catalog_text": (
            "📦 *የኢንዱስትሪ የጎማ ሶል ምርቶች ዝርዝር*\n\n"
            "ለረጅም ጊዜ አገልግሎት፣ ለጠንካራ መያዣ (Traction) እና ለከፍተኛ ጫና የማይበገሩ። "
            "ቴክኒካዊ መግለጫዎችን እና ምስሎችን ለማየት ከታች አንዱን ይምረጡ፦"
        ),
        "product_1": "🥾 የሥራ ቦት ጫማ ሶል (Work Boot)",
        "product_2": "👟 የዕለት ተዕለት ካዥዋል ሶል (Casual TR)",
        "product_3": "🏃 የስፖርት ጫማ ሶል አሃድ (Athletic Unit)",
        "custom_text": (
            "🛠️ *Custom Mold እና ሶል ማምረቻ አገልግሎት*\n\n"
            "እንደ ድርጅትዎ ፍላጎትና ዲዛይን ትክክለኛ የጎማ ሞልዶችን እናዘጋጃለን። የንድፍ ሐሳብዎን፣ "
            "የሚፈልጉትን መጠን እና ዝርዝር መረጃ በመላክ ከኛ ጋር ይስሩ።"
        ),
        "factory_text": (
            "🏭 *የፋብሪካችን ምርት እና ጥራት ቁጥጥር*\n\n"
            "በአዲስ አበባ በሚገኘው ማምረቻችን ዘመናዊ የሙቀት ማጣሪያ (Vulcanization) ቴክኖሎጂዎችን በመጠቀም "
            "ለአገር ውስጥ እና ለቀጣናው የጫማ አምራቾች ጥራት ያላቸው ምርቶችን እናቀርባለን።"
        ),
        "contact_text": (
            "📞 *የድርጅቱ የሽያጭ እና የኮርፖሬት ማዕከል*\n\n"
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
            "prod_2": ("Casual TR & Rubber Sole Unit", "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800&auto=format&fit=crop&q=80"),
            "prod_3": ("Athletic & Trainer Sole Unit", "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800&auto=format&fit=crop&q=80"),
        }
        p_name, p_img = prod_names[data]
        caption = f"📦 *{p_name}*\n\n• High-grade durable rubber compound.\n• Superior slip and abrasion resistance.\n• Custom color matching & hardness options available for bulk manufacturing."
        
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


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = os.getenv("CHANNEL_ID")
    if not channel_id:
        if update.message:
            await update.message.reply_text("Error: CHANNEL_ID environment variable not set.")
        return

    broadcast_caption = (
        "🔔 *Zemen Shoe Manufacturing PLC - Corporate Update*\n\n"
        "Supplying premium-grade molded rubber soles and industrial shoe components to manufacturers and partners across East Africa.\n\n"
        "📍 *Location:* Addis Ababa, Ethiopia\n"
        "📞 *Direct Sales:* +251 900 000 000\n"
        "🤖 *Interactive Catalog Bot:* @ZemenShoes_Bot\n\n"
        "#RubberSoles #CustomSoles #B2BFootwear #ZemenShoes #MadeInEthiopia"
    )
    
    banner_url = "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80"

    try:
        await context.bot.send_photo(
            chat_id=channel_id,
            photo=banner_url,
            caption=broadcast_caption,
            parse_mode="Markdown"
        )
        if update.message:
            await update.message.reply_text("✅ Catalog update successfully broadcasted to the official channel.")
    except Exception as e:
        logger.error(f"Failed to broadcast: {e}")
        if update.message:
            await update.message.reply_text(f"❌ Broadcast failed: {e}")


async def fn_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.warning("WARNING: Please set a valid TELEGRAM_BOT_TOKEN environment variable.")
        
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(fn_error)

    logger.info("Zemen Shoe Manufacturing Bot is running smoothly...")
    app.run_polling()


if __name__ == "__main__":
    main()
