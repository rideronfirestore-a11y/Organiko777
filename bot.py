unoimport asyncio
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import (
    BOT_TOKEN,
    ADMIN_ID,
    NEQUI,
    BREB,
)


PRODUCTS = {
    "verde_10": {
        "name": "🟢 Camiseta Verde 10G",
        "price": 20000,
        "stock": 10,
    },
    "verde_20": {
        "name": "🟢 Camiseta Verde 20G",
        "price": 40000,
        "stock": 10,
    },
    "verde_65": {
        "name": "🟢 Camiseta Verde 65G",
        "price": 90000,
        "stock": 10,
    },
    "blanca_1": {
        "name": "⚪ Camiseta Blanca 1G",
        "price": 20000,
        "stock": 10,
    },
    "blanca_3": {
        "name": "⚪ Camiseta Blanca 3G",
        "price": 50000,
        "stock": 10,
    },
    "morada_1": {
        "name": "🟣 Camiseta Morada 1G",
        "price": 50000,
        "stock": 10,
    },
}


PENDING_PAYMENTS = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🌿 Bienvenido a Orgánico 11 🌿

Hola 👋
Es un gusto tenerte aquí.

Contamos con productos disponibles de forma rápida, organizada y segura ✅

📍 Selecciona una opción para continuar.
"""

    keyboard = [
        [InlineKeyboardButton("📦 Ver catálogo", callback_data="catalogo")],
        [InlineKeyboardButton("💳 Métodos de pago", callback_data="pagos")],
        [InlineKeyboardButton("📞 Soporte", callback_data="soporte")],
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalogo":
        keyboard = []

        for key, product in PRODUCTS.items():
            if product["stock"] > 0:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{product['name']} — ${product['price']:,}",
                        callback_data=f"buy_{key}",
                    )
                ])

        await query.message.reply_text(
            "🌿 Catálogo disponible",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "pagos":
    elif query.data == "pagos":
    texto_pago = f"""
💳 MÉTODOS DE PAGO

💛 Nequi: {NEQUI}

💳 Bre-B: {BREB}

📸 Envía el comprobante para continuar.
"""

    await query.message.reply_text(texto_pago)

elif query.data == "soporte":
    await query.message.reply_text(
        "📞 Soporte Orgánico 11 disponible."
    )

    elif query.data.startswith("buy_"):
        product_key = query.data.replace("buy_", "")
        product = PRODUCTS[product_key]

        PENDING_PAYMENTS[query.from_user.id] = product_key

        text = f"""
🛒 Pedido seleccionado

📦 Producto:
{product['name']}

💵 Valor:
${product['price']:,}

💳 Realiza el pago y envía el comprobante.

Nequi: {NEQUI}
Bre-B: {BREB}
"""

        await query.message.reply_text(text)


async def comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in PENDING_PAYMENTS:
        return

    product_key = PENDING_PAYMENTS[user_id]
    product = PRODUCTS[product_key]

    caption = f"""
💰 Nuevo pago pendiente

👤 Usuario:
{update.effective_user.first_name}

📦 Producto:
{product['name']}

💵 Valor:
${product['price']:,}
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirmar pedido",
                callback_data=f"approve_{user_id}_{product_key}",
            )
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    await update.message.reply_text(
        "⏳ Tu comprobante fue recibido correctamente."
    )


async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("No autorizado", show_alert=True)
        return

    await query.answer()

    if query.data.startswith("approve_"):
        parts = query.data.split("_")

        user_id = int(parts[1])
        product_key = parts[2]

        product = PRODUCTS[product_key]

        if product["stock"] <= 0:
            await query.message.reply_text("❌ Sin stock disponible")
            return

        product["stock"] -= 1

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
✅ Pago confirmado

📦 Producto:
{product['name']}

Gracias por tu compra en Orgánico 11 🌿
""",
        )

        await query.message.reply_text(
            f"✅ Pedido aprobado.
📦 Stock restante: {product['stock']}"
        )


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = "📦 Stock actual

"

    for product in PRODUCTS.values():
        text += f"{product['name']} → {product['stock']} disponibles
"

    await update.message.reply_text(text)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = "🌿 Panel Administrador Orgánico 11"

    await update.message.reply_text(text)


async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("stock", stock))

    app.add_handler(CallbackQueryHandler(admin_buttons, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(MessageHandler(filters.PHOTO, comprobante))

    print("🤖 Orgánico 11 activo...")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
