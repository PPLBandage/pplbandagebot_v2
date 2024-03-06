from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods import DeleteWebhook
from prisma import Prisma
import os
import asyncio
from dotenv import load_dotenv
import datetime, pytz
import math
import time
import client
from io import BytesIO
import keyboards

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
db = Prisma()


class States(StatesGroup):
    """Стейты для aiogram"""
    wait_to_skin = State()
    wait_to_color = State()
    wait_to_review = State()
    wait_to_support = State()
    wait_to_support_answer = State()


async def render_and_edit(client: client.Client, state: FSMContext):
    skin_rer = await client.rerender()
    bio = BytesIO()
    bio.name = "render.png"
    skin_rer.save(bio, "PNG")
    bio.seek(0)

    photo = types.BufferedInputFile(file=bio.read(), filename="render.png")
    preview_id: types.Message = (await state.get_data()).get("prewiew_id")
    try:
        msg = await bot.edit_message_media(types.input_media_photo.InputMediaPhoto(media=photo, 
                                                                                   caption=preview_id.caption, 
                                                                                   parse_mode="Markdown"), 
                                           chat_id=preview_id.chat.id,
                                           message_id=preview_id.message_id,
                                           reply_markup=preview_id.reply_markup)
        await state.update_data(prewiew_id=msg)
    except:
        pass


@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    """Хэндлер для команды /start"""

    await state.clear()
    caption_text = "Привет👋! Давай начнём.\nОтправь мне свой ник или развёртку скина *как файл*"
        
    msg = await message.answer_photo(
        photo=FSInputFile(f"res/presets/start.png"),
        caption=caption_text,
        parse_mode="Markdown"
    )
    await state.update_data(prewiew_id=msg)
    await state.update_data(client=client.Client())
    await state.set_state(States.wait_to_skin)


@dp.message(Command('support'))
async def support(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Отмена", callback_data="review_deny"))
    message = await message.answer("Хорошо, теперь отправьте мне одно сообщение с вопросом (можно фото)", reply_markup=builder.as_markup())
    await state.update_data(review_message=message)
    await state.set_state(States.wait_to_support)


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


@dp.message(F.text, States.wait_to_skin)
async def skin_nick(message: types.Message, state: FSMContext):
    await message.delete()

    _client: client.Client = (await state.get_data()).get("client", None)
    mc_class = client.Player(name=message.text)  # create a Player object by UUID
    await mc_class.initialize()  # Fetch player data
    if mc_class._raw_skin == None:  # If player not found
        message = await message.answer("Аккаунт с таким именем не найден(")
        asyncio.create_task(client.delete_message(message, 5))
        return
    
    _client.raw_skin = mc_class._raw_skin.convert("RGBA")
    _client.default_skin = _client.raw_skin.copy()

    width, height = _client.raw_skin.size
    if width != 64 and (height != 64 or height != 32):
        message = await message.answer("Извините, скин имеет неподдерживаемый формат")
        asyncio.create_task(client.delete_message(message, 5))
        return

    if width == 64 and height == 32:  # If skin is below 1.8
        _client.raw_skin = _client.default_skin = client.to64(_client.raw_skin)

    if client.check_skin_background(_client.raw_skin):  # Check skin background
        message = await message.answer("У вашего скина непрозрачный фон!\nПредпросмотр может быть некорректным!")
        asyncio.create_task(client.delete_message(message, 10))
    
    _client.average_color = client.average_color(_client.default_skin)

    await render_and_edit(_client, state)
    builder = await keyboards.main_menu()
    settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    await settings_message.edit_caption(reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.set_state(state=None)  # clear state

    if not bool(_client.raw_skin.getpixel((46, 52))[3]) and not bool(_client.raw_skin.getpixel((45, 52))[3]):
        builder = await keyboards.build_manual_skin_selection()
        message = await settings_message.edit_caption(caption="Извините, боту не удалось корректно определить тип вашего скина.\nПожалуйста, выберете правильный:", 
                                                      reply_markup=builder.as_markup(), 
                                                      parse_mode="Markdown")
        await state.update_data(messages=message)


@dp.message(F.document, States.wait_to_skin)
async def skin_file(message: types.Message, state: FSMContext):
    await message.delete()
    _client: client.Client = (await state.get_data()).get("client", None)

    document = message.document
    file_id = document.file_id
    bio = BytesIO()
    file_bytes = await bot.download(file_id, destination=bio)
    bio.seek(0)
    
    _client.raw_skin = client.Image.open(file_bytes).convert("RGBA")
    _client.default_skin = _client.raw_skin.copy()

    width, height = _client.raw_skin.size
    if width != 64 and (height != 64 or height != 32):
        message = await message.answer("Это не развёртка скина! Развёртка должна иметь размеры 64х64 пикселя")
        asyncio.create_task(client.delete_message(message, 5))
        return
    if width == 64 and height == 32:  # If skin is below 1.8
        _client.raw_skin = _client.default_skin = client.to64(_client.raw_skin)

    if client.check_skin_background(_client.raw_skin):  # Check skin background
        message = await message.answer("У вашего скина непрозрачный фон!\nПредпросмотр может быть некорректным!")
        asyncio.create_task(client.delete_message(message, 10))
    
    _client.average_color = client.average_color(_client.default_skin)

    await render_and_edit(_client, state)
    builder = await keyboards.main_menu()
    settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    await settings_message.edit_caption(reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.set_state(state=None)  # clear state

    if not bool(_client.raw_skin.getpixel((46, 52))[3]) and not bool(_client.raw_skin.getpixel((45, 52))[3]):
        builder = await keyboards.build_manual_skin_selection()
        message = await settings_message.edit_caption(caption="Извините, боту не удалось корректно определить тип вашего скина.\nПожалуйста, выберете правильный:", 
                                                      reply_markup=builder.as_markup(), 
                                                      parse_mode="Markdown")
        await state.update_data(messages=message)


@dp.message(F.photo, States.wait_to_skin)
async def skin_file(message: types.Message, state: FSMContext):
    await message.delete()
    message = await message.answer("Пожалуйста, отправьте скин *как файл*", parse_mode="Markdown")
    asyncio.create_task(client.delete_message(message, 5))


@dp.callback_query(F.data.startswith("manual_"))
async def manual_select_slim(callback: types.CallbackQuery, state: FSMContext):
    slim = callback.data.replace("manual_", "").split("-")
    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(callback.message)
        return
    
    _client.manual_slim = 1 if slim[0] == "steve" else 2
    _client.slim = False if slim[0] == "steve" else True

    await render_and_edit(_client, state)

    settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    if slim[1] == "main_menu":
        builder = await keyboards.main_menu()
        await settings_message.edit_caption(reply_markup=builder.as_markup(), parse_mode="Markdown")
        return
    elif slim[1] == "main_settings":
        builder, caption = await keyboards.main_settings(_client)
        message = await settings_message.edit_caption(caption=caption, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.update_data(prewiew_id=message)
        return


@dp.callback_query(F.data.startswith("keyboard_"))
async def keyb(callback: types.CallbackQuery, state: FSMContext):
    settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    if not settings_message:
        await callback.message.answer("Извините, не удалось найти сообщение с настройками!\nПожалуйста, отправьте /start и попробуйте снова")
        return

    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(callback.message)
        return

    builder: InlineKeyboardBuilder = None
    caption: str = None
    match callback.data.replace("keyboard_", ""):
        case "main_menu":
            builder = await keyboards.main_menu()
            await state.set_state(None)
        case "style_select":
            caption = "Выберите стиль"
            builder = await keyboards.style_select()
            await state.set_state(None)
        case "shape_main":
            caption = "Выберите стиль"
            builder = await keyboards.shape_select()
        case "another_authors":
            caption = "Выберите стиль"
            builder = await keyboards.another_authors() 
        case "kwixie":
            caption = "Выберите стиль"
            builder = await keyboards.kwixie()
        case "pwgood_main":
            caption = "Выберите стиль"
            builder = await keyboards.pwgood()
        case "default_colors":
            caption = "Выберите стиль"
            builder = await keyboards.default_colors()
        case "custom_color":
            caption = "Теперь отправьте свой цвет в формате **HEX** или **RGB**\nЦвет можно получить на сайте ниже\n" + \
            "Бот принимает цвета в форматах:\n" + \
            "#ffffff\nffffff\n255,255,255\n255, 255, 255 и т.п."
            builder = await keyboards.custom_color()
            await state.set_state(States.wait_to_color)
        case "general_settings":
            builder, caption = await keyboards.main_settings(_client)
        case "view_settings":
            builder, caption = await keyboards.view_settings(_client)
        case "save":
            caption = "Выберите, что сохранить:"
            builder = await keyboards.save()

    message = await settings_message.edit_caption(caption=caption, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.update_data(prewiew_id=message)


@dp.callback_query(F.data.startswith("ps_"))
async def style_select_ps(callback: types.CallbackQuery, state: FSMContext):
    _pepe = callback.data.replace("ps_", "")
    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(callback.message)
        return
    _client.pepe_image_id = _pepe
    _client.custom_color = (0, 0, 0)
    
    image = client.Image.open(f"res/pepes/colored/{_pepe}.png").convert("RGBA")
    h = image.size[1]
    _client.pepe_height = h
    _client.change_range = 12 - h
    await render_and_edit(_client, state)


@dp.callback_query(F.data.startswith("pc_"))
async def style_select_pc(callback: types.CallbackQuery, state: FSMContext):
    _color = callback.data.replace("pc_", "")
    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(callback.message)
        return
    colours = [
            (61, 58, 201),  # Blue
            (176, 30, 30),  # Red
            (85, 163, 64),  # Yellow
            (250, 213, 30),  # Green
            (252, 15, 192),  # Pink
            (105, 0, 198),  # Violet
            (255, 102, 0),  # Orange
            (255, 255, 255),  # White
            (0, 0, 0),  # Black
        ]
    _client.custom_color = colours[int(_color)]
    _client.pepe_image_id = None
    await render_and_edit(_client, state)


@dp.message(F.text, States.wait_to_color)
async def custom_color(message: types.Message, state: FSMContext):
    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(message)
        return
    await message.delete()
    await state.set_state(None)
    message_context = message.text.lstrip("#")
    input1 = message_context.split(", ")
    input2 = message_context.split(",")

    try:
        if len(input1) == 1 and len(input2) == 1:
            colour = tuple(int(message_context[i : i + 2], 16) for i in (0, 2, 4))
        else:
            if len(input1) == 1:
                colour = (int(input2[0]), int(input2[1]), int(input2[2]))
            else:
                colour = (int(input1[0]), int(input1[1]), int(input1[2]))
        _client.custom_color = colour
        _client.pepe_image_id = None
        await render_and_edit(_client, state)
    except:
        message = await message.answer("Не удалось получить цвет\nПопробуйте ещё раз")
        asyncio.create_task(client.delete_message(message, 10))


@dp.callback_query(F.data.startswith("sett_"))
async def general_settings(callback: types.CallbackQuery, state: FSMContext):
    _setting = callback.data.replace("sett_", "")
    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(callback.message)
        return
    return_to_settings = True
    match _setting:
        case "up":
            _client.position = max(0, _client.position - 1)
        case "down":
            _client.position = min(_client.position + 1, _client.change_range)
        case "fl":
            _client.first_layer += 1
            if _client.first_layer > 2:
                _client.first_layer = 0
        case "delpix":
            _client.clear_pixeles = not _client.clear_pixeles
        case "overlay":
            _client.overlay = not _client.overlay
        case "skintype":
            builder: InlineKeyboardBuilder = await keyboards.build_manual_skin_selection("main_settings")
            settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
            message = await settings_message.edit_caption(caption="Выберите тип скина:", reply_markup=builder.as_markup(), parse_mode="Markdown")
            await state.update_data(prewiew_id=message)
            return
        case "bodypart":
            _client.body_part += 1
            if _client.body_part > 3:
                _client.body_part = 0
        case "pepetype":
            _client.pepe_type += 1
            if _client.pepe_type > len(_client.pepes) - 1:
                _client.pepe_type = 0
        case "back":
            return_to_settings = False
            _client.back_view = not _client.back_view
        case "pose":
            return_to_settings = False
            _client.pose += 1
            if _client.pose > len(client.poses[0]) - 1:
                _client.pose = 0
        case "reset_view":
            return_to_settings = False
            _client.back_view = False
            _client.pose = 0

    await render_and_edit(_client, state)

    settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    builder, caption = (await keyboards.main_settings(_client)) if return_to_settings else (await keyboards.view_settings(_client))
    message = await settings_message.edit_caption(caption=caption, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.update_data(prewiew_id=message)


@dp.callback_query(F.data == "finish")
async def finish(callback: types.CallbackQuery, state: FSMContext):
    settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    builder = await keyboards.finish()
    message = await settings_message.edit_caption(caption="Заврешить? После завершения отредактировать скин будет невозможно!", 
                                                  reply_markup=builder.as_markup(), 
                                                  parse_mode="Markdown")
    await state.update_data(prewiew_id=message)


@dp.callback_query(F.data.startswith("download_"))
async def save_handler(callback: types.CallbackQuery, state: FSMContext):
    _setting = callback.data.replace("download_", "")
    _settings_message: types.Message = (await state.get_data()).get("prewiew_id", None)
    _client: client.Client = (await state.get_data()).get("client", None)
    if not _client:
        await client.sessionPizda(callback.message)
        return
    
    bio = BytesIO()
    match _setting:
        case "skin":
            bio.name = "skin.png"
            _client.raw_skin.save(bio, "PNG")
            bio.seek(0)
            photo = types.BufferedInputFile(file=bio.read(), filename="skin.png")
            await callback.message.answer_document(photo, caption="Готовый скин")
            await callback.answer()
        case "bandage":
            bio.name = "bandage.png"
            _client.bandage.save(bio, "PNG")
            bio.seek(0)
            photo = types.BufferedInputFile(file=bio.read(), filename="bandage.png")
            await callback.message.answer_document(photo, caption="Повязка")
            await callback.answer()
        case "json":
            data = types.BufferedInputFile(file=_client.export_JSON().encode("utf-8"), filename="settings.json")
            await callback.message.answer_document(data, caption="Файл настроек")
            await callback.answer()
        case "finish_confirm":
            await _settings_message.delete()
            await state.clear()



# -------------------- REVIEWS --------------------


async def generate_reviews_page(page: int, admin: bool) -> str:
    reviews = await db.review.find_many(take=5, skip=page * 5, order={"id": "desc"})

    content = "Отзывы:\n"
    for review in reviews:
        user = await db.user.find_first(where={"user_id": review.user_id})
        try:
            member_full_name = (await bot.get_chat_member(review.user_id, review.user_id)).user.full_name
        except:
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
    builder.row(types.InlineKeyboardButton(text="Отмена", callback_data=f"review_deny"))
    await callback.message.edit_text(text="Теперь опишите работу бота *одним* сообщением", 
                                     parse_mode="Markdown",
                                     reply_markup=builder.as_markup())


@dp.message(F.text, States.wait_to_review)
async def review_create(message: types.Message, state: FSMContext):
    _stars: int = int((await state.get_data()).get("stars", 0))
    now_time = datetime.datetime.now(pytz.timezone("Etc/GMT-3"))
    now_time_format = "{}.{}.{} {}:{}".format(
        client.null_add(now_time.day),
        client.null_add(now_time.month),
        now_time.year,
        client.null_add(now_time.hour),
        client.null_add(now_time.minute),
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

# ----------------------- SUPPORT ------------------------


@dp.message(States.wait_to_support)
async def support_send(message: types.Message, state: FSMContext):
    await bot.forward_message(-1001980044675, message.chat.id, message.message_id)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Ответить", callback_data=f"answer_{message.from_user.id}"))
    await bot.send_message(
                chat_id=-1001980044675,
                text=f"От {message.from_user.full_name} {message.from_user.id}",
                parse_mode="Markdown",
                reply_markup=builder.as_markup())
    await message.answer("Принято!")
    await (await state.get_data()).get("review_message").delete()
    await state.clear()


@dp.callback_query(F.data.startswith("answer_"))
async def support_answer(callback: types.CallbackQuery, state: FSMContext):
    _user_id: int = int(callback.data.replace("answer_", ""))
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Отмена", callback_data="review_deny"))
    message = await callback.message.answer("Отправьте ответ", reply_markup=builder.as_markup())
    await state.update_data(review_message=message)
    await state.update_data(user_support_id=_user_id)
    await state.set_state(States.wait_to_support_answer)


@dp.message(States.wait_to_support_answer)
async def support_send_answer(message: types.Message, state: FSMContext):
    _user_id: int = int((await state.get_data()).get("user_support_id"))
    await bot.forward_message(_user_id, message.chat.id, message.message_id)

    await message.answer("Принято!")
    await (await state.get_data()).get("review_message").delete()
    await state.clear()


@dp.callback_query(F.data.startswith("user_"))
async def save_handler(callback: types.CallbackQuery, state: FSMContext):
    _setting = callback.data.replace("user_", "")

    if _setting.startswith("delete"):
        review_id = int(_setting.replace("delete_", ""))
        await db.review.delete(where={'id': review_id})
        await callback.answer("Удалено!")
        return

    if _setting.startswith("ban"):
        user_id = int(_setting.replace("ban_", ""))
        user = await db.user.find_first(where={"user_id": user_id})
        if user:
            await db.user.update(where={"id": user.id}, data={"banned": True})
            await callback.answer("Забанен!")
            return
        await db.user.create(data={
            "user_id": user_id,
            "banned": True
        })
        await callback.answer("Забанен!")

    if _setting.startswith("unban"):
        user_id = int(_setting.replace("unban_", ""))
        user = await db.user.find_first(where={"user_id": user_id})
        if user:
            await db.user.update(where={"id": user.id}, data={"banned": False})
            await callback.answer("Разбанен!")
            return


# -------------------- END OF SUPPORT --------------------


async def start_bot():
    """Асинхронная функция для запуска диспатчера"""
    
    await db.connect()  # Connecting to database
    started = True
    while started:
        try:
            await bot(DeleteWebhook(drop_pending_updates=True))
            await dp.start_polling(bot)
            started = False
        except:
            started = True
            print("An error has occurred, reboot in 10 seconds")
            time.sleep(10)
            print("rebooting...")


if __name__ == '__main__':
    asyncio.run(start_bot())