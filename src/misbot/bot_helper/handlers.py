import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from misbot.config import ADMIN_USER_ID
from misbot.constans import HELLO_MESSAGE, STATE_QUESTION, STATE_ANSWER
from misbot.database import exec as db


async def helper_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELLO_MESSAGE)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data.startswith("page_"):
        page = int(callback_data.split("_")[1])
        context.user_data["current_page"] = page
        await helper_get_info(update, context, page)

    elif callback_data.startswith("question_"):
        info_block = await db.get_info_block(
            int(callback_data.split("_")[1])
        )
        await query.message.reply_text(
                f"*Вопрос:* {info_block["question"]}\n\n"
                f"*Ответ:*\n{info_block["answer"]}",
                parse_mode="Markdown"
            )


async def helper_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != ADMIN_USER_ID:
        await update.message.reply_text(
            "У вас не достаточно прав для создания записи"
        )
        return
    context.user_data["creation_state"] = STATE_QUESTION
    context.user_data["creation_data"] = {}
    await update.message.reply_text(
        "Начало создание info блока\n\n"
        "Шаг 1 из 2: Введите вопрос"
    )


async def handle_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["creation_state"] == STATE_QUESTION:
        context.user_data["creation_data"]["question"] = update.message.text
        context.user_data["creation_state"] = STATE_ANSWER
        await update.message.reply_text(
            "Вопрос сохранен\n\n"
            "Шаг 2 из 2: Введите ответ",
        )
    elif context.user_data["creation_state"] == STATE_ANSWER:
        context.user_data["creation_data"]["answer"] = update.message.text

        try:
            await db.create_info_block(**context.user_data["creation_data"])
            await update.message.reply_text("Info блок успешно создан!")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при сохранении: {e}")
            logging.error(f"Error creating info block: {e}")
        del context.user_data["creation_state"]
        del context.user_data["creation_data"]


async def helper_get_info(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int= 1):
    questions = await db.get_info_blocks(page)
    if questions == "ERROR:404":
        await update.message.reply_text("Вопросы не найдены")
        return
    records_per_page = 5
    total_pages = (
        (await db.get_info_blocks_count() + records_per_page - 1)
        // records_per_page
    )
    keyboard = []
    for question in questions:
        question_text = question["question"]
        if len(question_text) > 30:
            question_text = question_text[:30] + "..."
        button = InlineKeyboardButton(
            text=question_text,
            callback_data=f"question_{question["id"]}"
        )
        keyboard.append([button])
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = f"Страница {page} из {total_pages}\nВыберите вопрос:"
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup
        )


handler_creation_text = MessageHandler(
    filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
    handle_creation
)
handler_start = CommandHandler("start", helper_start)
handler_create = CommandHandler("create", helper_create)
handler_info = CommandHandler("info",  helper_get_info)
handler_callback = CallbackQueryHandler(button_callback)
