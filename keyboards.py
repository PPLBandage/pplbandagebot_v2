from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


async def reviews(now_page: int, left: bool = True, right: bool = True) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if left:
        builder.add(types.InlineKeyboardButton(text="«", callback_data=f"revButton_{now_page - 1}"))
    if right:
        builder.add(types.InlineKeyboardButton(text="»", callback_data=f"revButton_{now_page + 1}"))
    return builder


async def review() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="5", callback_data="createReview_5"),
                types.InlineKeyboardButton(text="4", callback_data="createReview_4"),
                types.InlineKeyboardButton(text="3", callback_data="createReview_3"),
                types.InlineKeyboardButton(text="2", callback_data="createReview_2"),
                types.InlineKeyboardButton(text="1", callback_data="createReview_1"))
    builder.row(types.InlineKeyboardButton(text="Продолжить без оценки", callback_data="createReview_0"))
    builder.row(types.InlineKeyboardButton(text="Отмена", callback_data="review_deny"))
    return builder
