from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создаем главную клавиатуру с двумя кнопками
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Парсер"),
            KeyboardButton(text="Калькулятор")
        ]
    ],
    resize_keyboard=True,  # Кнопки будут подстраиваться под размер экрана
    input_field_placeholder="Выберите нужное действие"  # Текст-подсказка в строке ввода
)
