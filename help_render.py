from PIL import Image, ImageFont, ImageDraw
from os.path import isfile, join
from os import listdir
import random


def render() -> Image.Image:
    # Drawing a person
    base = Image.open("res/presets/help.png")
    persons = [f for f in listdir("res/persons/help") if isfile(join("res/persons/help", f))]
    name = random.choice(persons)
    person = Image.open(f"res/persons/help/{name}")
    base.paste(person, (0, 0), person)
    person.close()
    
    # Drawing a person nickname
    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype('res/font.otf', 30)  
    text = name.replace(".png", "")
    draw.text((5, 1040), text, font = font, align ="left", fill="black")  
        
    return base
