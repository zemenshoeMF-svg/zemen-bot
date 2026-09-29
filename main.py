
import os
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

async def send_catalog_update(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE = None):
    bot = Bot(token=TOKEN)

    # Full multi-language catalog text with product details and branding
    caption = (
        "🌼 **ዘምልም የረንጅ መስደል ድልድል በድል!** 🌼\n"
        "የዘይመን ጫማ ማምረቻ ፋብሪካ (Zemen Shoe Manufacturing PLC) ለውድ የንግድ አጋሮቻችን፣ "
        "ለጫማ አምራቾች፣ ለደንበኞቻችን እና ለመላው የክርስትናና የእምነት ተከታዮች እንኳን አደረሰዎት!\n\n"
        "-------------------------------------\n\n"
        "🔔 **Zemen Shoe Manufacturing PLC - B2B Catalog Update**\n\n"
        "We supply high-quality custom molded rubber soles and shoe molds for factories and industrial partners.\n\n"
        "📍 **Location:** Addis Ababa, Ethiopia\n"
        "📞 **Phone:** +251 911 24 54 57\n"
        "🤖 **Assistant Bot:** @ZemenShoes_Bot\n\n"
        "#RubberSoles #CustomSoles #B2BFootwear #ZemenShoes"
    )

    # You can attach your product photo file_id or image URL here
    photo_file_id = "AgACAgQAAxkBAAFVOYpqvEbIfn_rSwWUtyRV8ui5MIuU3gAC6xBrG-vCwFEKVmUJHaOw4wEAAwIAA3kAAz0E"

    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo_file_id,
        caption=caption,
        parse_mode="Markdown"
    )
    
    if update and update.message:
        await update.message.reply_text("Full multi-language catalog broadcasted successfully!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("broadcast", send_catalog_update))
    app.run_polling()

if __name__ == "__main__":
    main()
