import random
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import logging
from pathlib import Path
from tai_card_promo_key import token
from aiogram.types import ParseMode
from aiogram.utils.markdown import hspoiler

bot = Bot(token)
dp = Dispatcher(bot)
numask = 0
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    image_file = Path("img","hi.jpg")
    #print("print3")
    img_path = image_file

    caption = (
    f"Привет!\n"
    f"Меня зовут Сиам-Сиам. Я бот для изучения тайского языка.\n" 
    f"В платной версии ты найдёшь больше вопросов, звуков и ассоциативных картинок.\n"  
    f'Переходи на @SiamSiam_bot.')
     # Отправляем изображение с описанием обратно пользователю
    with open(img_path, "rb") as photo:
        await bot.send_photo(message.chat.id, photo=photo, caption=caption)   
    await handle_next_question(message)

#@dp.message_handler(commands=["sendpayinformation___"])
@dp.message_handler(commands=[""])
async def handle_next_question(message: types.Message):
    global numask 
    # Получаем слова из базы данных
    cursor.execute("SELECT COUNT(*) FROM words")
    (rows,) = cursor.fetchone()
    print("rows= ", int(rows))
   # numask = random.randint(1, rows - 1)
    numask += 1
    if numask > rows:
        numask = 1
    #numask = 10    здесь можно задать номер записи
    print("numask= ", numask)
    cursor.execute(
        "SELECT num, tai, transkript, translate, butn1, butn2, butn3, butn4 FROM words WHERE num = ?",
        (numask,),
    )
    row = cursor.fetchone()
    image_file = Path("img", str(numask) + ".jpg")
    print("row= ", row)
    if row:
        num, tai, transkript, translate, butn1, butn2, butn3, butn4 = row
        conn.commit()
        print("translate= ", translate)
           # Создаем клавиатуру с 4 кнопками
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_word1 = types.InlineKeyboardButton(
            text=butn1, callback_data=f"compare_{translate}_{butn1}"
        )
        button_word2 = types.InlineKeyboardButton(
            text=butn2, callback_data=f"compare_{translate}_{butn2}"
        )
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_word3 = types.InlineKeyboardButton(
            text=butn3, callback_data=f"compare_{translate}_{butn3}"
        )
        button_word4 = types.InlineKeyboardButton(
            text=str(butn4), callback_data= "compare_" + str(translate) + "_" + str(butn4)
        )
        keyboard.add(button_word1, button_word2, button_word3, button_word4)
        image_file = Path("img", str(numask) + ".jpg")
        img_path = image_file
        with open(img_path, "rb") as photo:
            await bot.send_photo(chat_id=message.chat.id, photo=photo)
        with open(Path("sound", str(numask) + ".ogg"), "rb") as audio:
            await bot.send_audio(chat_id=message.chat.id, audio=audio)
            hidden_text = hspoiler(transkript)
        await message.answer(
            f"{numask}  Выберите правильный перевод:\n  {tai} \n {hidden_text}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer("Извините, в базе нет такой строки, наберите /start ")
        #print("print6 /n")

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("compare_"))
async def compare_words(callback_query: types.CallbackQuery):
    # Разбиваем данные из callback на составляющие
    _, btn, translated = callback_query.data.split("_")
    if btn == translated:
        await callback_query.answer("Правильный ответ!", False)
        await handle_next_question(callback_query.message)
    else:
        await callback_query.answer("Неправильный ответ", False)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
