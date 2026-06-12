from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from bot.keyboards import main_keyboard
from infrastructure.database import crud
import os

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    
    # Обработка реферальной ссылки (например, t.me/bot?start=ref123)
    referrer_id = None
    args = command.args
    if args and args.startswith("ref"):
        try:
            referrer_id = int(args.replace("ref", ""))
            # Защита от самореферальства
            if referrer_id == message.from_user.id:
                referrer_id = None
        except ValueError:
            pass

    # Регистрируем/получаем пользователя в БД
    await crud.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        referrer_id=referrer_id
    )
    
    webapp_url = os.getenv("WEBAPP_URL", "http://localhost:8000")
    
    # Кнопка для открытия Mini App
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url=webapp_url))]
    ])

    await message.answer(
        "Добро пожаловать в приложение!\nНажмите кнопку ниже, чтобы начать обучение и работу с Китаем.",
        reply_markup=markup
    )

# --- Обработка кнопок администратора ---
@router.callback_query(F.data.startswith("pay_approve_"))
async def process_payment_approve(callback: CallbackQuery, bot: Bot):
    payment_id = int(callback.data.split("_")[2])
    success = await crud.approve_payment(payment_id)
    if success:
        await callback.message.edit_text(callback.message.text + "\n\n✅ Одобрено!")
        await callback.answer("Платеж одобрен")
        # Здесь можно добавить уведомление самому пользователю об успешной оплате
    else:
        await callback.answer("Ошибка или платеж уже обработан")

@router.callback_query(F.data.startswith("pay_reject_"))
async def process_payment_reject(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[2])
    success = await crud.reject_payment(payment_id)
    if success:
        await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонено!")
        await callback.answer("Платеж отклонен")
    else:
        await callback.answer("Ошибка или платеж уже обработан")
