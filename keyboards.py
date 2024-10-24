from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import client


async def build_manual_skin_selection(callback: str = "main_menu") -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Стив", callback_data=f"manual_steve-{callback}"))
    builder.add(types.InlineKeyboardButton(text="Алекс", callback_data=f"manual_alex-{callback}"))
    return builder


async def main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🎨 Выбрать стиль повязки", callback_data="keyboard_style_select"))
    builder.add(types.InlineKeyboardButton(text="⚙️ Основные настройки", callback_data="keyboard_general_settings"))
    builder.add(types.InlineKeyboardButton(text="👀 Настройки отображения", callback_data="keyboard_view_settings"))
    builder.add(types.InlineKeyboardButton(text="⬇️ Сохранить", callback_data="keyboard_save"))
    builder.adjust(1)
    return builder


async def style_select() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Повязки Шейп", callback_data="keyboard_shape_main"))
    builder.row(types.InlineKeyboardButton(text="Повязки от других авторов", callback_data="keyboard_another_authors"))
    builder.row(types.InlineKeyboardButton(text="Повязки Пугода", callback_data="keyboard_pwgood_main"))
    builder.row(types.InlineKeyboardButton(text="Стандартные цвета", callback_data="keyboard_default_colors"))
    builder.row(types.InlineKeyboardButton(text="🎨 Кастомный цвет", callback_data="keyboard_custom_color"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def shape_select() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Золотой", callback_data="ps_gold"),
                types.InlineKeyboardButton(text="Серебряный", callback_data="ps_silver"))
    builder.row(types.InlineKeyboardButton(text="ModErator", callback_data="ps_moder"),
                types.InlineKeyboardButton(text="Космонавт", callback_data="ps_space"))
    builder.row(types.InlineKeyboardButton(text="Панк", callback_data="ps_pank"),
                types.InlineKeyboardButton(text="Барби", callback_data="ps_barbie"))
    builder.row(types.InlineKeyboardButton(text="Бендер", callback_data="ps_bender"), 
                types.InlineKeyboardButton(text="Рилавеон", callback_data="ps_rlbl"))
    builder.row(types.InlineKeyboardButton(text="Монохромная", callback_data="ps_mono"), 
                types.InlineKeyboardButton(text="Негатив", callback_data="ps_nega"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_style_select"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def another_authors() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="kwixie_", callback_data="keyboard_kwixie"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_style_select"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def kwixie() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Пепе в гирляндах", callback_data="ps_gr"),
                types.InlineKeyboardButton(text="Ледяная пепе", callback_data="ps_ice"))
    builder.row(types.InlineKeyboardButton(text="Пепе с цветком", callback_data="ps_flower"),
                types.InlineKeyboardButton(text="Пепе на чёрно-зелёной подкладке", callback_data="ps_green_kwix"))
    builder.row(types.InlineKeyboardButton(text="PepeS", callback_data="ps_kwix_1"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_another_authors"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def pwgood() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Повязка Пугода", callback_data="ps_pw"))
    builder.row(types.InlineKeyboardButton(text="Старая повязка Пугода", callback_data="ps_pw_old"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_style_select"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def default_colors() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Синий", callback_data="pc_0"),
                types.InlineKeyboardButton(text="Красный", callback_data="pc_1"),
                types.InlineKeyboardButton(text="Зелёный", callback_data="pc_2"))
    builder.row(types.InlineKeyboardButton(text="Жёлтый", callback_data="pc_3"),
                types.InlineKeyboardButton(text="Розовый", callback_data="pc_4"),
                types.InlineKeyboardButton(text="Фиолетовый", callback_data="pc_5"))
    builder.row(types.InlineKeyboardButton(text="Оранжевый", callback_data="pc_6"),
                types.InlineKeyboardButton(text="Белый", callback_data="pc_7"),
                types.InlineKeyboardButton(text="Чёрный", callback_data="pc_8"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_style_select"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def custom_color() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Сайт", url="https://colorscheme.ru/color-converter.html"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_style_select"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def main_settings(_client: client.Client) -> client.Tuple[InlineKeyboardBuilder, str]:
    builder = InlineKeyboardBuilder()
    if not _client.pepe_image_id:
        pepe_type_button = types.InlineKeyboardButton(text="Тип пепе", callback_data="sett_pepetype")
    else:
        pepe_type_button = types.InlineKeyboardButton(text="ㅤ", callback_data="pass")
    
    builder.row(types.InlineKeyboardButton(text="↑", callback_data="sett_up"),
                types.InlineKeyboardButton(text="Первый слой", callback_data="sett_fl"),
                types.InlineKeyboardButton(text="Удаление пикселей над повязкой", callback_data="sett_delpix"))
    builder.row(types.InlineKeyboardButton(text=f"{_client.position}/{_client.change_range}", callback_data="pass"),
                types.InlineKeyboardButton(text="Оверлей", callback_data="sett_overlay"),
                types.InlineKeyboardButton(text="Версия скина", callback_data="sett_skintype"))
    builder.row(types.InlineKeyboardButton(text="↓", callback_data="sett_down"),
                types.InlineKeyboardButton(text="Часть тела", callback_data="sett_bodypart"),
                pepe_type_button)
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))

    body = ["Левая рука", "Левая нога", "Правая рука", "Правая нога"]
    version_txt = "Алекс" if _client.slim else "Стив"
    overlay_txt = "Вкл" if _client.overlay else "Выкл"
    first_layer_txt = ["Выкл", "Подкладка", "Дублирование повязки"][_client.first_layer]
    
    content = f"*Версия скина:* {version_txt}\n" + \
              f"*Оверлей:* {overlay_txt}\n" + \
              f"*Первый слой:* {first_layer_txt}\n" + \
              f"*Часть тела:* {body[_client.body_part]}\n" + \
              f"*Удаление пикселей над повязкой:* {'Вкл' if _client.clear_pixels else 'Выкл'}\n"
    return builder, content


async def view_settings(_client: client.Client) -> client.Tuple[InlineKeyboardBuilder, str]:
    builder = InlineKeyboardBuilder()
    
    builder.row(types.InlineKeyboardButton(text=f"Вид {'сзади' if not _client.back_view else 'спереди'}", callback_data="sett_back"))
    builder.row(types.InlineKeyboardButton(text="Поза", callback_data="sett_pose"))
    builder.row(types.InlineKeyboardButton(text="Сброс вида", callback_data="sett_reset_view"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))

    back_txt = "Вкл" if _client.back_view else "Выкл"
    pose_txt = ["Нормальная", "Бег", "Ходьба", "Зарядка", "Зарядка снизу"][_client.pose]
    
    content = f"*Вид сзади:* {back_txt}\n" + \
              f"*Поза:* {pose_txt}"
    
    return builder, content


async def save() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Скачать готовый скин", callback_data="download_skin"))
    builder.row(types.InlineKeyboardButton(text="Скачать только повязку", callback_data="download_bandage"))
    builder.row(types.InlineKeyboardButton(text="Завершить настройку", callback_data="finish"))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data="keyboard_main_menu"))
    return builder


async def finish() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Завершить настройку", callback_data="download_finish_confirm"))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data="keyboard_save"))
    return builder


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
