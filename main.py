import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Bot Token from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# --- ASSET & MEDIA URLS (Mapped from your uploaded brand files) ---
ASSETS = {
    "welcome": "https://i.ibb.co/3s7H2v9/1000401874.png",          # Brand Logo
    "catalog": "https://i.ibb.co/6y4b2qL/1000401746.jpg",          # Rubber Outsole Technical Banner
    "rubber": "https://i.ibb.co/9V3h3fP/1000401531.jpg",           # Production Line / Soles
    "custom": "https://i.ibb.co/8m1z2x5/1000401876.jpg",           # Future Mold & Tech Design
    "services": "https://i.ibb.co/5L2p8k3/1000401543.jpg",         # Factory Floor Showcase
    "location": "https://i.ibb.co/4g9J2q7/1000400191.png",         # Google Maps & Factory Layout
    "qr": "https://i.ibb.co/2M7x9v6/1000401846.png"                # Location QR Code
}

# --- USER SESSIONS (Temporary memory for registration and ordering) ---
user_languages = {}  # {user_id: 'am' or 'en'}
user_states = {}     # Tracks if user is registering, ordering, or reporting

# ==================== /start COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_languages[user_id] = 'am'  # Default to Amharic
    
    keyboard = [
        [InlineKeyboardButton("🇪🇹 አማርኛ (Amharic)", callback_data="lang_am"), InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("👟 የራበር ሶል ካታሎግ | Catalog", callback_data="menu_catalog")],
        [InlineKeyboardButton("📝 እንደ ደንበኛ ይመዝገቡ | Register Client", callback_data="register_client")],
        [InlineKeyboardButton("📦 ትዕዛዝ ይስጡ | Place Bulk Order", callback_data="place_order")],
        [InlineKeyboardButton("🛡️ የውል ምስጢራዊነት (NDA) | Security", callback_data="menu_services")],
        [InlineKeyboardButton("📍 የፋብሪካ አድራሻ | Location & QR", callback_data="menu_location")],
        [InlineKeyboardButton("📢 የቴሌግራም ቻናል ይቀላቀሉ | Join Channel", callback_data="join_channel")],
        [InlineKeyboardButton("📞 የሽያጭ ክፍል | Contact B2B", callback_data="menu_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        "🇪🇹 <b>እንኳን ወደ ዘመን ጫማ ማኑፋክቸሪንግ ኃ.የተ.የግ.ማ በደህና መጡ!</b>\n"
        "<i>\"ጽኑ ሶል፣ ትልቅ እርምጃ!\"</i>\n\n"
        "የወንዶች የራበር ሶል አምራች | በቻይናውያን ባለሙያዎች የሚመራ | ለጫማ ፋብሪካዎች የሚሆን የራበር ሶል እና የሞልድ ሥራ | አዲስ አበባ\n\n"
        "-------------------------------\n"
        "🇬🇧 <b>Welcome to Zemen Shoe Manufacturing PLC</b>\n"
        "<i>B2B Men's Shoe Soles Manufacturer | Chinese Expert-Led | Custom Rubber & Molds</i>\n\n"
        "👇 <i>ቋንቋ ይምረጡ ወይም ከታች ያሉትን አማራጮች ይጠቀሙ / Select an option below:</i>"
    )
    
    if update.message:
        await update.message.reply_photo(photo=ASSETS["welcome"], caption=caption, parse_mode="HTML", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_photo(photo=ASSETS["welcome"], caption=caption, parse_mode="HTML", reply_markup=reply_markup)

# ==================== LANGUAGE TOGGLE ====================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "lang_am":
        user_languages[user_id] = 'am'
        await query.edit_message_caption(caption="✅ ቋንቋ ወደ አማርኛ ተቀይሯል። ከታች ካሉት አማራጮች ይምረጡ:", parse_mode="HTML")
    else:
        user_languages[user_id] = 'en'
        await query.edit_message_caption(caption="✅ Language switched to English. Choose an option below:", parse_mode="HTML")
    
    await start(update, context)

# ==================== CATALOG & PRODUCTS ====================
async def catalog_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "👟 <b>Zemen B2B Rubber Sole Catalog / የራበር ሶል ካታሎግ</b>\n\n"
        "1️⃣ <b>High-Volume Vulcanized Rubber Soles</b>\n"
        "• ለኢንዱስትሪ ደህንነት እና ለቀን ጫማዎች የሚሆን 100% የራበር ውህድ።\n\n"
        "2️⃣ <b>Custom Rubber Outsoles & Mold Tooling</b>\n"
        "• በራሳችሁ ብራንድ፣ ሎጎ እና ስታይል የሚሰራ የሞልድ ስራ በጥብቅ NDA።\n\n"
        "👇 <i>ምርቶቹን ለመመልከት ይጫኑ / Select below:</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👞 Standard Rubber Soles", callback_data="prod_rubber")],
        [InlineKeyboardButton("🛠️ Custom Molds & Tooling", callback_data="prod_custom")],
        [InlineKeyboardButton("◀️️ Main Menu / ዋና ገጽ", callback_data="main_menu")]
    ])
    await query.message.reply_photo(photo=ASSETS["catalog"], caption=text, parse_mode="HTML", reply_markup=keyboard)

async def prod_rubber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "👞 <b>High-Volume Vulcanized Rubber Outsoles</b>\n\n"
        "• <b>Compound:</b> 100% High-Grade Vulcanized Rubber Matrix.\n"
        "• <b>Performance:</b> Exceptional abrasion resistance & flex endurance.\n"
        "• <b>Safety:</b> Oil-resistant, anti-slip tread profiles.\n\n"
        "🇪🇹 ለጫማ ፋብሪካዎች የምርት መስመር በብዛት የሚቀርብ አስተማማኝ የራበር ሶል።"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Place Order / ትዕዛዝ ስጡ", callback_data="place_order")],
        [InlineKeyboardButton("◀️️ Back / ተመለስ", callback_data="menu_catalog")]
    ])
    await query.message.reply_photo(photo=ASSETS["rubber"], caption=text, parse_mode="HTML", reply_markup=keyboard)

async def prod_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🛠️ <b>Custom Rubber Outsoles & Mold Tooling</b>\n\n"
        "• <b>Brand Customization:</b> Your factory logo and custom sizing runs.\n"
        "• <b>Strict NDA:</b> Your proprietary molds are used exclusively for you.\n\n"
        "🇪🇹 የርሶን ልዩ ንድፍ በቻይናውያን ባለሙያዎች ትክክለኛነት እናመራለን።"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Request Custom Mold / የሞልድ ትዕዛዝ", callback_data="place_order")],
        [InlineKeyboardButton("◀️ Back / ተመለስ", callback_data="menu_catalog")]
    ])
    await query.message.reply_photo(photo=ASSETS["custom"], caption=text, parse_mode="HTML", reply_markup=keyboard)

# ==================== CLIENT REGISTRATION ====================
async def register_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_states[user_id] = "waiting_for_contact"
    
    # Request phone number button
    contact_button = KeyboardButton(text="📱 ስልክ ቁጥሬን አጋራ / Share Contact", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.reply_text(
        "📝 <b>እንደ ፋብሪካ/ደንበኛ ለመመዝገብ</b>\n\n"
        "እባክዎ ከታች ያለውን <b>'ስልክ ቁጥሬን አጋራ'</b> የሚለውን ቁልፍ በመጫን ስልክዎን ያጋሩ።\n\n"
        "<i>Please tap the button below to share your phone number and complete B2B client registration.</i>",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if user_states.get(user_id) == "waiting_for_contact":
        phone_number = update.message.contact.phone_number
        user_states[user_id] = "registered"
        
        await update.message.reply_text(
            f"✅ <b>ምዝገባዎ ተጠናቋል! (Registration Successful)</b>\n\n"
            f"ስም: {user.full_name}\n"
            f"ስልክ: {phone_number}\n\n"
            "አሁን የራበር ሶል ትዕዛዝ መስጠት ወይም ከሽያጭ ክፍላችን ጋር መነጋገር ይችላሉ።",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup([], remove_keyboard=True)
        )

# ==================== ORDER INTAKE ====================
async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📦 <b>B2B Bulk Order & Custom Inquiry / የትዕዛዝ ማመልከቻ</b>\n\n"
        "ትዕዛዝዎን ለመጀመር እባክዎ በቀጥታ በስልክ ቁጥሮቻችን ያነጋግሩን ወይም በዋትስአፕ ይጻፉልን፡\n\n"
        "📞 <b>ስልክ:</b> +251 911 719 676 / +251 911 245 457\n"
        "💬 <b>WhatsApp:</b> https://wa.me/251911719676\n"
        "📧 <b>Email:</b> zemenshoemanufacturing@gmail.com"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Chat on WhatsApp", url="https://wa.me/251911719676")],
        [InlineKeyboardButton("📞 Call Sales Hotline", url="tel:+251911719676")],
        [InlineKeyboardButton("◀️ Main Menu / ዋና ገጽ", callback_data="main_menu")]
    ])
    await query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# ==================== SECURITY & SERVICES ====================
async def services_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🛡️ <b>Security, Quality Control & NDA Protection</b>\n\n"
        "• <b>Chinese Expert-Led:</b> Overseen by senior rubber compounding engineers.\n"
        "• <b>Complete NDA Protection:</b> Legal confidentiality safeguarding your designs.\n"
        "• <b>Isolated Mold Vaults:</b> Zero risk of unauthorized replication.\n\n"
        "🇪🇹 የርስዎ የሶል ንድፍ በውል የተጠበቀ እና ለሶስተኛ ወገን የማይሰጥ መሆኑን እናረጋግጣለን።"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Main Menu / ዋና ገጽ", callback_data="main_menu")]])
    await query.message.reply_photo(photo=ASSETS["services"], caption=text, parse_mode="HTML", reply_markup=keyboard)

# ==================== LOCATION & QR ====================
async def location_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📍 <b>Factory Location & Google Maps</b>\n\n"
        "<b>Zemen Shoe Manufacturing PLC</b>\n"
        "Addis Ababa, Ethiopia (Beyond Shewa Market / Abebeche Building Area)\n\n"
        "🗺️ <i>Scan the QR code or tap the button below for direct map navigation.</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Open Google Maps", url="https://maps.app.goo.gl/y1VoGfmMfwen1vLa8")],
        [InlineKeyboardButton("⭐ Google Review", url="https://search.google.com/local/writereview?placeid=ChIJ4XGOQieFSxYR5d0RqiYShLI")],
        [InlineKeyboardButton("◀️ Main Menu / ዋና ገጽ", callback_data="main_menu")]
    ])
    # Send QR code image first, then details
    await query.message.reply_photo(photo=ASSETS["qr"], caption="📷 <b>Zemen Official Location QR Code</b>", parse_mode="HTML")
    await query.message.reply_photo(photo=ASSETS["location"], caption=text, parse_mode="HTML", reply_markup=keyboard)

# ==================== CHANNEL INVITE & CONTACT ====================
async def join_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "📢 <b>የዘመን ጫማ ማኑፋክቸሪንግ ኦፊሴላዊ ቻናል ይቀላቀሉ!</b>\n\nዕለታዊ የምርት ዝመናዎችን እና አዳዲስ የሶል ዲዛይኖችን ይከታተሉ።"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/ZemenShoes_Bot")],
        [InlineKeyboardButton("◀️ Main Menu / ዋና ገጽ", callback_data="main_menu")]
    ])
    await query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def contact_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📞 <b>Contact Zemen B2B Sales & Engineering</b>\n\n"
        "• <b>Phones:</b> +251 911 719 676 / +251 911 245 457\n"
        "• <b>WhatsApp:</b> https://wa.me/251911719676\n"
        "• <b>Email:</b> zemenshoemanufacturing@gmail.com\n"
        "• <b>Location:</b> Addis Ababa (Beyond Shewa Market)"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Main Menu / ዋና ገጽ", callback_data="main_menu")]])
    await query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# ==================== MAIN APPLICATION ROUTER ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command & Callback Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(catalog_menu, pattern="^menu_catalog$"))
    app.add_handler(CallbackQueryHandler(prod_rubber, pattern="^prod_rubber$"))
    app.add_handler(CallbackQueryHandler(prod_custom, pattern="^prod_custom$"))
    app.add_handler(CallbackQueryHandler(register_client, pattern="^register_client$"))
    app.add_handler(CallbackQueryHandler(place_order, pattern="^place_order$"))
    app.add_handler(CallbackQueryHandler(services_menu, pattern="^menu_services$"))
    app.add_handler(CallbackQueryHandler(location_menu, pattern="^menu_location$"))
    app.add_handler(CallbackQueryHandler(join_channel, pattern="^join_channel$"))
    app.add_handler(CallbackQueryHandler(contact_menu, pattern="^menu_contact$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    
    # Contact Share Handler
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    print("🚀 Zemen Enterprise B2B Bot is fully active and deployed...")
    app.run_polling()

if __name__ == "__main__":
    main()
