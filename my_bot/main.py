import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from prompts import PROMPTS, SCIENTIST_WIKI
from keyboards import main_menu, back_menu, exam_answers, scientists_menu
from wiki import get_wiki_summary

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_states = {}

ERRORS = {
    "prof":     "😴 Даже мой мозг иногда отдыхает... Попробуй ещё раз, троечник!",
    "survival": "🏃 Профессор ушёл домой! Попробуй ещё раз!",
    None:       "❌ Что-то пошло не так. Попробуй ещё раз!"
}

@dp.message(CommandStart())
async def start(message: types.Message):
    uid = message.from_user.id
    user_states[uid] = {"mode": None, "history": [], "stress": 0}
    name = message.from_user.first_name
    await message.answer(
        f"👋 Привет, {name}!\n\n"
        "🎓 Добро пожаловать в *ВЫЖИВШИЙ СТУДЕНТ*\n"
        "Три режима. Один шанс. Удачи.\n\n"
        "Выбери режим 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

MENU_BUTTONS = [
    "😈 Вредный Профессор",
    "💀 Попробуй Выживи: Экзамен",
    "⏳ Учение-Мучение: Вне Времени",
    "🔙 Назад в меню"
]

SCIENTIST_BUTTONS = list(SCIENTIST_WIKI.keys())

@dp.message(lambda m: m.text in MENU_BUTTONS)
async def menu_handler(message: types.Message):
    uid = message.from_user.id
    text = message.text

    if text == "🔙 Назад в меню":
        user_states[uid] = {"mode": None, "history": [], "stress": 0}
        await message.answer("🔙 Возвращаемся в главное меню!", reply_markup=main_menu())
        return

    user_states[uid] = {"mode": None, "history": [], "stress": 0}

    if text == "😈 Вредный Профессор":
        user_states[uid]["mode"] = "prof"
        await message.answer(
            "😈 *Режим ВРЕДНЫЙ ПРОФЕССОР активирован*\n\n"
            "Скидывай свой код или задавай вопрос...\n"
            "Посмотрим насколько всё плохо 🔍",
            reply_markup=back_menu(), parse_mode="Markdown"
        )

    elif text == "💀 Попробуй Выживи: Экзамен":
        user_states[uid]["mode"] = "survival"
        await message.answer(
            "💀 *Симулятор экзамена загружается...*\n😰 Уровень стресса: 0%",
            reply_markup=exam_answers(), parse_mode="Markdown"
        )
        await generate_reply(message, uid, "Начни игру! Опиши напряжённую атмосферу перед экзаменом и задай первый вопрос с вариантами A, B, C, D.")

    elif text == "⏳ Учение-Мучение: Вне Времени":
        user_states[uid]["mode"] = "choosing_scientist"
        await message.answer(
            "⏳ *Временной портал открывается...*\n\n"
            "Выбери с кем хочешь поговорить 👇",
            reply_markup=scientists_menu(), parse_mode="Markdown"
        )

@dp.message(lambda m: m.text in SCIENTIST_BUTTONS)
async def scientist_handler(message: types.Message):
    uid = message.from_user.id
    text = message.text

    mode_key, wiki_query = SCIENTIST_WIKI[text]
    user_states[uid] = {"mode": mode_key, "history": [], "stress": 0}

    wiki_fact = get_wiki_summary(wiki_query)

    await message.answer(
        f"⏳ *Портал открыт! Соединяемся с {text}...*",
        reply_markup=back_menu(), parse_mode="Markdown"
    )

    trigger = (
        f"Представься торжественно как {wiki_query}. "
        f"Расскажи кратко о себе используя эти реальные факты: {wiki_fact}. "
        f"Говори строго в стиле своей эпохи с первого слова!"
    )
    await generate_reply(message, uid, trigger)

@dp.message()
async def chat_handler(message: types.Message):
    uid = message.from_user.id

    if uid not in user_states or not user_states[uid]["mode"]:
        await message.answer("👇 Сначала выбери режим из меню!", reply_markup=main_menu())
        return

    if user_states[uid]["mode"] == "choosing_scientist":
        await message.answer("👇 Выбери учёного из списка!", reply_markup=scientists_menu())
        return

    user_text = message.text
    mode = user_states[uid]["mode"]

    extra_context = ""
    if mode == "prof":
        keywords = ["декарт", "ньютон", "эйнштейн", "ломоносов", "пифагор", "тесла"]
        for kw in keywords:
            if kw in user_text.lower():
                extra_context = f"\n[Справка из Википедии]: {get_wiki_summary(kw)}"
                break

    await generate_reply(message, uid, user_text + extra_context)

async def generate_reply(message: types.Message, uid: int, user_text: str):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    mode = user_states[uid]["mode"]
    system_prompt = PROMPTS[mode]

    user_states[uid]["history"].append({"role": "user", "content": user_text})
    messages_to_send = [{"role": "system", "content": system_prompt}] + user_states[uid]["history"]

    try:
        response = await asyncio.to_thread(
            requests.post,
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_NAME,
                "messages": messages_to_send,
                "temperature": 0.8,
                "max_tokens": 1000
            },
            timeout=30
        )

        reply = response.json()["choices"][0]["message"]["content"]

        if mode == "survival":
            if any(w in reply.lower() for w in ["неверно", "неправильно", "ошибка", "провал"]):
                user_states[uid]["stress"] = min(100, user_states[uid]["stress"] + 20)
            stress = user_states[uid]["stress"]
            stress_bar = f"\n\n😰 Уровень стресса: {stress}%"
            if stress >= 100:
                stress_bar = "\n\n💀 СТРЕСС 100%! ВЫ ПРОВАЛИЛИСЬ!\nНапиши /start чтобы начать заново."
            reply += stress_bar

        user_states[uid]["history"].append({"role": "assistant", "content": reply})

        if len(user_states[uid]["history"]) > 15:
            user_states[uid]["history"] = user_states[uid]["history"][-15:]

        await message.answer(reply)

    except Exception as e:
        error_msg = ERRORS.get(mode, ERRORS[None])
        await message.answer(error_msg)
        print(f"Ошибка: {e}")

async def main():
    print("🤖 Бот ВЫЖИВШИЙ СТУДЕНТ запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())