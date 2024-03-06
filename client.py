from minePi.player import Player
from minePi.skin import Skin
from PIL import Image, ImageOps
from typing import Tuple, List
import asyncio

body_part_x = [32, 16, 40, 0]
body_part_y = [52, 52, 20, 20]
body_part_x_overlay = [48, 0, 40, 0]
body_part_y_overlay = [52, 52, 36, 36]

poses = [
    [0,  20, 10, 0, 0], # vrll
    [0, -20,-10, 0, 0], # vrrl
    [0, -20,-10, 0, 0], # vrla
    [0,  20, 10, 0, 0], # vrra
    [0,   0,  0, 90, 90], # hrla
    [0,   0,  0, -90, -90], # hrra
    [0,   0,  0, 20, 20], # hrll
    [0,   0,  0, -20, -20], # hrrl
    [-20, -20, -20, -20, 40]  # vr
]


async def delete_message(message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    try:
        await message.delete()
    except:
        pass


async def sessionPizda(msg):
    await msg.answer("Упс. Ваша сессия была завершена\nПожалуйста, отправьте /start для начала работы")


def null_add(number: int) -> str:
    if number < 10:
        number = "0" + str(number)
    return str(number)


def check_skin_background(skin: Image.Image) -> bool:
    for y_ch in range(3):  # Simple check for transparent background
        for x_ch in range(3):
            t = skin.getpixel((x_ch, y_ch))[3]
            if t != 0:
                return True
    return False


def paste(img: Image.Image, img_to_paste: Image.Image, pos: Tuple[float, float]) -> Image.Image:
    _img = img.copy()
    _img_to_paste = img_to_paste.copy()
    width, height = _img_to_paste.size
    for y in range(height):
        for x in range(width):
            r, g, b, t = _img_to_paste.getpixel((x, y))
            try:
                _img.putpixel((x + pos[0], y + pos[1]), (r, g, b, t))
            except:
                pass
    return _img


def average_color(image: Image.Image) -> Tuple[int, int, int]:
    image = image.copy().convert("RGBA")
    width, height = image.size
    r_a, g_a, b_a, num = 0, 0, 0, 0
    for y in range(height):
        for x in range(width):
            r, g, b, t = image.getpixel((x, y))
            if t != 0:
                r_a += r
                g_a += g
                b_a += b
                num += 1
    
    if num == 0: return (255, 255, 255)
    return (255 - round(r_a / num), 255 - round(g_a / num), 255 - round(b_a / num))


def fill(image: Image.Image, color: Tuple[int, int, int]) -> Image.Image:
    image = image.copy().convert("RGBA")
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r, g, b, t = image.getpixel((x, y))
            try:
                if t != 0 and r == g == b: 
                    image.putpixel((x, y), (round((r / 255) * color[0]), round((g / 255) * color[1]), round((b / 255) * color[2]), t))
            except:
                pass
    return image


def clear(image: Image.Image, pos: Tuple[int, int], height: int) -> Image.Image:
    image = image.copy().convert("RGBA")
    for y in range(height):
        for x in range(16):
            try:
                image.putpixel((x + pos[0], y + pos[1]), (0, 0, 0, 0))
            except:
                pass
    return image


def crop_pepe(filename: str, body_part: int, slim: bool, height: int) -> Image.Image:
    image = Image.open(filename).convert("RGBA")
    if slim and (body_part == 0 or body_part == 2): 
        result_image = image.crop((0, 0, 15, height + 1))
    else: 
        result_image = image.copy()

    if body_part > 1:
        img_left = result_image.crop((0, 0, 8, height))
        img_right = result_image.crop((8, 0, 16, height))
        
        result_image = Image.new('RGBA', (16, height), (0, 0, 0, 0))
        result_image = paste(result_image, img_right, (0, 0))
        paste_position = 8 if not (slim and (body_part == 0 or filename == "res/pepes/pepe_1.png" or body_part == 2)) else 6
        result_image = paste(result_image, img_left, (paste_position, 0))
    return result_image


def to64(skin: Image.Image) -> Image:
    new_img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    img = skin.copy()
    leg = img.crop((0, 16, 16, 32))
    arm = img.crop((40, 16, 64, 32))

    new_img.paste(leg, (16, 48), leg)
    new_img.paste(arm, (32, 48), arm)
    new_img.paste(img, (0, 0), img)

    leg_1 = img.crop((0, 20, 4, 32))
    leg_1 = ImageOps.mirror(leg_1)
    new_img.paste(leg_1, (24, 52), leg_1)

    leg_2 = img.crop((8, 20, 12, 32))
    leg_2 = ImageOps.mirror(leg_2)
    new_img.paste(leg_2, (16, 52), leg_2)

    leg_2 = img.crop((4, 20, 8, 32))
    leg_2_m = ImageOps.mirror(leg_2)
    new_img.paste(leg_2_m, (20, 52), leg_2_m)

    leg_2 = img.crop((12, 20, 16, 32))
    leg_2_m = ImageOps.mirror(leg_2)
    new_img.paste(leg_2_m, (28, 52), leg_2_m)

    leg_2 = img.crop((4, 16, 8, 20))
    leg_2_m = ImageOps.mirror(leg_2)
    new_img.paste(leg_2_m, (20, 48), leg_2_m)

    leg_2 = img.crop((8, 16, 12, 20))
    leg_2_m = ImageOps.mirror(leg_2)
    new_img.paste(leg_2_m, (24, 48), leg_2_m)

    arm_1 = img.crop((40, 20, 44, 32))
    arm_1 = ImageOps.mirror(arm_1)
    new_img.paste(arm_1, (40, 52), arm_1)

    arm_1 = img.crop((48, 20, 52, 32))
    arm_1 = ImageOps.mirror(arm_1)
    new_img.paste(arm_1, (32, 52), arm_1)

    arm_1 = img.crop((44, 20, 48, 32))
    arm_1_m = ImageOps.mirror(arm_1)
    new_img.paste(arm_1_m, (36, 52), arm_1_m)

    arm_1 = img.crop((52, 20, 56, 32))
    arm_1_m = ImageOps.mirror(arm_1)
    new_img.paste(arm_1_m, (44, 52), arm_1_m)

    arm_1 = img.crop((44, 16, 48, 20))
    arm_1_m = ImageOps.mirror(arm_1)
    new_img.paste(arm_1_m, (36, 48), arm_1_m)

    arm_1 = img.crop((48, 16, 52, 20))
    arm_1_m = ImageOps.mirror(arm_1)
    new_img.paste(arm_1_m, (40, 48), arm_1_m)
    return new_img


class Client:
    def __init__(self):
        self.slim: bool = None  # Skin is slim
        self.manual_slim: int = 0  # Manually set slim of skin
        self.raw_skin: Image.Image = None  # Raw skin
        self.default_skin: Image.Image = None  # Default skin
        self.average_color: Tuple[int, int, int] = None  # Average color of skin

        # ------- Settings -------
        self.position: int = 4  # Position of pepe
        self.custom_color: Tuple[int, int, int] = (255, 255, 255)  # Custom color
        self.pepe_image_id: int = None  # Id of pepe preset
        self.first_layer: int = 1  # First layer state
        self.overlay: bool = True  # Overlay state
        self.body_part: int = 0  # Part of body (leg/arm)
        self.clear_pixeles: bool = True  # Clear pixeles under the lining
        self.pepe_type: int = 0  # default pepe type
        self.change_range: int = 8  # Range of pepe position
        self.pepe_height: int = 4  # Height of pepe
        self.back_view: int = False  # Back view
        self.pose: int = 0  # Pose id
        self.pepes: List[str] = ["pepe.png", "pepe_1.png"]
        self.bandage: Image.Image = None  # Bandage image

    async def rerender(self):
        self.position = min(self.position, self.change_range)
        self.raw_skin = self.default_skin.copy() 
        if self.custom_color:
            if self.clear_pixeles:  # Clear pixeles uder the pepe
                self.raw_skin = clear(self.raw_skin.copy(), (body_part_x_overlay[self.body_part], body_part_y_overlay[self.body_part] + self.position), self.pepe_height)

            if not self.pepe_image_id:  # If pepe is default type
                pepe = crop_pepe("res/pepes/" + str(self.pepes[self.pepe_type]), self.body_part, self.slim, self.pepe_height)
                pepe = fill(pepe.copy(), self.custom_color)
            else:
                pepe = crop_pepe(f"res/pepes/colored/{self.pepe_image_id}.png", self.body_part, self.slim, self.pepe_height)
            sl = self.slim and not self.body_part
            cropped_pepe = pepe.crop((1, 0, 16, self.pepe_height)) if sl else pepe
            if self.first_layer == 2: 
                self.raw_skin.paste(cropped_pepe, (body_part_x[self.body_part], body_part_y[self.body_part] + self.position), cropped_pepe)
            if self.overlay:
                self.raw_skin.paste(cropped_pepe, (body_part_x_overlay[self.body_part], body_part_y_overlay[self.body_part] + self.position), cropped_pepe)

            self.bandage = Image.new('RGBA', (16, self.pepe_height), (0, 0, 0, 0))  # Create bandage for saving
            if self.first_layer == 1:  # If first laer is lining
                if not self.pepe_image_id:  # If pepe is default type
                    img_lining = Image.open("res/lining/custom.png").convert("RGBA")
                    img_lining = fill(img_lining.copy(), self.custom_color)
                else: 
                    img_lining = crop_pepe(f"res/lining/colored/{self.pepe_image_id}.png", self.body_part, self.slim, self.pepe_height)
                
                cropped_lining = img_lining.crop((2 if not self.pepe_image_id else 1, 0, 16, self.pepe_height)) if sl else img_lining
                self.raw_skin.paste(cropped_lining, (body_part_x[self.body_part], body_part_y[self.body_part] + self.position), cropped_lining)
                self.bandage.paste(img_lining, (0, 0), img_lining)  # paste lining in save bandage
                img_lining.close()
            self.bandage.paste(pepe, (0, 0), pepe)  # paste pepe in save bandage
            pepe.close()

        skin_object = Skin(self.raw_skin)

        hr = 45 if not self.back_view else 135
        if self.body_part <= 1:
            hr *= -1
        
        skin = await skin_object.render_skin(hr=hr, 
                                    vr=poses[8][self.pose], 
                                    ratio = 32, 
                                    vrc = 10, 
                                    vrll=poses[0][self.pose], 
                                    vrrl=poses[1][self.pose],
                                    vrla=poses[2][self.pose],
                                    vrra=poses[3][self.pose],
                                    hrla=poses[4][self.pose],
                                    hrra=poses[5][self.pose],
                                    hrll=poses[6][self.pose],
                                    hrrl=poses[7][self.pose],
                                    man_slim=self.manual_slim
                                    )
        
        skin_base = await skin_object.render_skin(hr=hr, 
                                    vr=poses[8][self.pose], 
                                    ratio = 32, 
                                    vrc = 10, 
                                    vrll=poses[0][self.pose], 
                                    vrrl=poses[1][self.pose],
                                    vrla=poses[2][self.pose],
                                    vrra=poses[3][self.pose],
                                    hrla=poses[4][self.pose],
                                    hrra=poses[5][self.pose],
                                    hrll=poses[6][self.pose],
                                    hrrl=poses[7][self.pose],
                                    man_slim=self.manual_slim,
                                    display_second_layer=False
                                    )
        self.raw_skin.putpixel((0, 3), (255, 0, 0, 255))
        self.raw_skin.putpixel((3, 3), (0, 255, 0, 255))
        self.raw_skin.putpixel((3, 0), (0, 0, 255, 255))
        
        width, height = skin.size
        width_1, height_1 = skin_base.size
        renderBack = Image.new(mode="RGBA", size=(height + 40, height + 40), color=self.average_color)
        renderBack.paste(skin_base, (round((height_1 + 40) / 2 - (width_1 / 2)), 20), skin_base)
        renderBack.paste(skin, (round((height + 40) / 2 - (width / 2)), 20), skin)
        return renderBack
