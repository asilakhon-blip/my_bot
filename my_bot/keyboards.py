from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="😈 Вредный Профессор")
    builder.button(text="💀 Попробуй Выживи: Экзамен")
    builder.button(text="⏳ Учение-Мучение: Вне Времени")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def back_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔙 Назад в меню")
    return builder.as_markup(resize_keyboard=True)

def exam_answers():
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ A")
    builder.button(text="✅ B")
    builder.button(text="✅ C")
    builder.button(text="✅ D")
    builder.button(text="🔙 Назад в меню")
    builder.adjust(4, 1)
    return builder.as_markup(resize_keyboard=True)

def scientists_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎩 Рене Декарт")
    builder.button(text="🍎 Исаак Ньютон")
    builder.button(text="⚡ Никола Тесла")
    builder.button(text="🧪 Мария Кюри")
    builder.button(text="💡 Альберт Эйнштейн")
    builder.button(text="🔭 Галилео Галилей")
    builder.button(text="🔙 Назад в меню")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)