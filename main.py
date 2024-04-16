"""
by AndcoolSystems, 2024
"""

__version__ = "final..."

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteWebhook
from aiogram.utils.markdown import link
from dotenv import load_dotenv
from prisma import Prisma
from io import BytesIO
import help_render
import keyboards
import datetime
import asyncio
import pytz
import math
import time
import os

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
db = Prisma()


class States(StatesGroup):
    """Стейты для aiogram"""
    wait_to_review = State()


def null_add(number: int) -> str:
    if number < 10:
        number = "0" + str(number)
    return str(number)



@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    """Хэндлер для команды /start"""

    await state.clear()
    await message.answer("*Поддержка Телеграм бота была завершена 2 июня 2024.*\nВместо этого используйте сайт: https://pplbandage.ru\n\n" + \
                         "Вы так же всё еще можете оставить отзыв о работе сайта здесь, отправив команду /review", parse_mode="Markdown")


@dp.message(Command('review'))
async def review(message: types.Message, state: FSMContext):
    await state.clear()
    builder: InlineKeyboardBuilder = await keyboards.review()
    user = await db.user.find_first(where={"user_id": message.from_user.id})
    if user and user.banned:
        await message.answer("Вы забанены в отзывах!\nМожете написать в /support и поддержка рассмотрит ваш запрос")
        return

    message = await message.answer("Хорошо, теперь оцените работу бота от *1* до *5*", 
                         parse_mode="Markdown",
                         reply_markup=builder.as_markup())
    await state.update_data(review_message=message)


@dp.message(Command('reviews'))
async def reviews(message: types.Message, state: FSMContext):
    await state.clear()
    builder: InlineKeyboardBuilder = await keyboards.reviews(0, left=False)
    await message.answer(await generate_reviews_page(0, message.chat.id == -1001980044675), 
                         parse_mode="Markdown",
                         reply_markup=builder.as_markup())
    

@dp.message(Command('help'))
async def help(message: types.Message, state: FSMContext):
    await state.clear()
    discord_link = link('Дискорд', 'https://discordapp.com/users/812990469482610729/')
    post_link = link('Пост', 'https://discord.com/channels/447699225078136832/1114275416404922388')
    shape_link = link('Шейп — Студия Minecraft', 'https://vk.com/shapestd')
    content = "PPL повязка - это бот, созданный для добавления повязки Пепеленда на ваш скин.\n" + \
    "*Поддержка бота официально прекращена! Это был прекрасный год, спасибо, что были с нами!.*\n" + \
    "*Вы можете воспользоваться сайтом для наложения повязок:* https://pplbandage.ru\n\n" + \
    f"При возникновении вопросов или ошибок обращайтесь в {discord_link}\nили *отправив команду* /support\n\n" + \
    f"*Текущая версия:* {__version__}\n" + \
    f"*Полезные ссылки:*\n{post_link} в идеях\n\n" + \
    f"*Created by AndcoolSystems, 2023\nПродакшн:* {shape_link}\n\n"

    donations = await db.donations.find_many(order={"value": "desc"})
    content += "*Люди, поддержавшие прект:*\n"
    for i, donation in enumerate(donations):
        content += f"*{i + 1}. {donation.nickname}* – {round(donation.value, 2)} *RUB*\n"

    image = help_render.render()
    bio = BytesIO()
    bio.name = "render.png"
    image.save(bio, "PNG")
    bio.seek(0)
    photo = types.BufferedInputFile(file=bio.read(), filename="render.png")

    await message.answer_photo(photo=photo, caption=content, parse_mode="Markdown")
    image.close()


# -------------------- REVIEWS --------------------


async def generate_reviews_page(page: int, admin: bool) -> str:
    reviews = await db.review.find_many(take=5, skip=page * 5, order={"id": "desc"})

    content = "Отзывы:\n"
    for review in reviews:
        user = await db.user.find_first(where={"user_id": review.user_id})
        try:
            member_full_name = (await bot.get_chat_member(review.user_id, review.user_id)).user.full_name
        except Exception:
            member_full_name = "Not found"

        username = member_full_name if not user or (user and not user.custom_nick) else user.custom_nick
        stars = ["", "★☆☆☆☆\n", "★★☆☆☆\n", "★★★☆☆\n", "★★★★☆\n", "★★★★★\n"]

        uid = f'({review.user_id}) ({review.id}) ' if admin else ''
        content += f"*{uid}{username}{user.badge if user else ''} {review.date}:*\n" + \
                   f"{stars[review.stars]}" + \
                   f"{review.message}\n\n"
        
    count = await db.review.count()
    content += f"*Страница* {page + 1}-{math.ceil(count / 5)}\n" + \
               "Оставить отзыв можно отправив команду /review"
    return content
    

@dp.callback_query(F.data.startswith("revButton_"))
async def reviews_button(callback: types.CallbackQuery, state: FSMContext):
    _page_num = int(callback.data.replace("revButton_", ""))
    count = await db.review.count()
    builder: InlineKeyboardBuilder = await keyboards.reviews(_page_num, left=_page_num != 0, right=_page_num != math.ceil(count / 5) - 1)
    await callback.message.edit_text(text=await generate_reviews_page(_page_num, callback.message.chat.id == -1001980044675), 
                                     parse_mode="Markdown",
                                     reply_markup=builder.as_markup())
    

@dp.callback_query(F.data.startswith("createReview_"))
async def review_stars(callback: types.CallbackQuery, state: FSMContext):
    _stars_count = int(callback.data.replace("createReview_", ""))
    await state.update_data(stars=_stars_count)
    await state.set_state(States.wait_to_review)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Отмена", callback_data="review_deny"))
    await callback.message.edit_text(text="Теперь опишите работу бота *одним* сообщением", 
                                     parse_mode="Markdown",
                                     reply_markup=builder.as_markup())


@dp.message(F.text, States.wait_to_review)
async def review_create(message: types.Message, state: FSMContext):
    _stars: int = int((await state.get_data()).get("stars", 0))
    now_time = datetime.datetime.now(pytz.timezone("Etc/GMT-3"))
    now_time_format = "{}.{}.{} {}:{}".format(
        null_add(now_time.day),
        null_add(now_time.month),
        now_time.year,
        null_add(now_time.hour),
        null_add(now_time.minute),
    )

    review = await db.review.create(data={"message": message.text,
                                 "stars": _stars,
                                 "user_id": message.from_user.id,
                                 "date": now_time_format})

    await message.answer("Готово! Посмотреть все отзывы можно отправив команду /reviews")

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Удалить отзыв", callback_data=f"user_delete_{review.id}"))
    builder.row(types.InlineKeyboardButton(text="Забанить", callback_data=f"user_ban_{message.from_user.id}"))
    builder.row(types.InlineKeyboardButton(text="Разбанить", callback_data=f"user_unban_{message.from_user.id}"))
    await bot.send_message(
                chat_id=-1001980044675,
                text=f"*{message.from_user.username}* оставил отзыв:\n" + \
                     f"{message.text}\n" + \
                     f"{_stars} звезды\n" + \
                     f"Его id: {message.from_user.id}",
                parse_mode="Markdown",
                reply_markup=builder.as_markup())
    
    await (await state.get_data()).get("review_message").delete()
    await message.delete()
    await state.clear()


@dp.callback_query(F.data == "review_deny")
async def review_deny(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# -------------------- END OF REVIEWS --------------------


async def start_bot():
    """Асинхронная функция для запуска диспатчера"""
    
    await db.connect()  # Connecting to database
    started = True
    while started:
        try:
            await bot(DeleteWebhook(drop_pending_updates=True))
            await dp.start_polling(bot)
            started = False
        except Exception:
            started = True
            print("An error has occurred, reboot in 10 seconds")
            time.sleep(10)
            print("rebooting...")


if __name__ == '__main__':
    asyncio.run(start_bot())