def check_coords(tl_coord, br_coord): #top left coord and bottom right coord
    '''
    Make sure that the top left coordinate is actually top left, and bottom right coord is actually bottom right
    '''
    if tl_coord.x > br_coord.x:
        tl_coord.x, br_coord.x = br_coord.x, tl_coord.x
    if tl_coord.y > br_coord.y:
        tl_coord.y, br_coord.y = br_coord.y, tl_coord.y
    return tl_coord, br_coord

def get_full_text_n_size(block):
    full_words = ""
    size = 0
    for paragraph in block.paragraphs:
        for word in paragraph.words:
            size = abs(word.bounding_box.vertices[0].y - word.bounding_box.vertices[2].y)
            for symbol in word.symbols:
                full_words+=symbol.text
                break_type = symbol.property.detected_break.type
                if break_type == 1:
                    full_words+=" "
                elif break_type == 5 or break_type == 3:
                    full_words+="\n"
    full_words += "@"
    return full_words, size

import io
import os
import googletrans

#Pillow Library that allows for image manipulation
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from googletrans import Translator

def translate_image(image_file, dest_lang, do_pronunciation):
    translator = Translator()
    #sets up GOOGLE_APPLICATION_CREDENTIALS 
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'menuTranslatorAuthentication.json'
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    #file_name = os.path.abspath(image_path)

    # Loads the image into memory
    # with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    text_anno = client.text_detection(image=image)
    text_blocks = text_anno.full_text_annotation.pages[0].blocks
    text_to_translate = ""
    text_sizes = []
    for block in text_blocks:
        text, text_size = get_full_text_n_size(block)
        text_to_translate+=text
        text_sizes.append(text_size)

    translated = translator.translate(text_to_translate, src = text_anno.text_annotations[0].locale, dest = dest_lang)
    translated_text_separated = translated.text.split('@')
    translated_text_separated.pop()
    try:
        pronunciation = translated.extra_data["translation"][len(translated.extra_data["translation"]) - 1][3]
        pronunciation_separated = ""
        if (pronunciation != None):
            pronunciation_separated = pronunciation.split('@')
            pronunciation_separated.pop()
        else:
            print("Pronunciation set to false because there is no available pronunciation")
            do_pronunciation = False
    except IndexError:
        print("Pronunciation set to false because there is no available pronunciation")
        do_pronunciation = False

    image = Image.open(image_file)
    draw = ImageDraw.Draw(image)
    for i in range(min(len(translated_text_separated), len(text_blocks))):
        #Get the verticies of the first and last word of the portion being translated
        top_left_vert = text_blocks[i].bounding_box.vertices[0]
        bot_right_vert = text_blocks[i].bounding_box.vertices[2]
        top_left_vert, bot_right_vert = check_coords(top_left_vert, bot_right_vert)
        #Crop and blur portion that's being translated
        cropped_img = image.crop((top_left_vert.x,top_left_vert.y,bot_right_vert.x,bot_right_vert.y))
        blurred_img = cropped_img.filter(ImageFilter.GaussianBlur(radius=8))
        image.paste(blurred_img, (top_left_vert.x,top_left_vert.y))
        #Set font size to the size of original text
        font_type = ImageFont.truetype('fonts/ARIALUNI.ttf', text_sizes[i])
        if do_pronunciation:
            #Draw outline of text
            draw.text(xy = (top_left_vert.x - 1, top_left_vert.y), text=pronunciation_separated[i], fill=(0,0,0), font = font_type)
            draw.text(xy = (top_left_vert.x + 1, top_left_vert.y), text=pronunciation_separated[i], fill=(0,0,0), font = font_type)
            draw.text(xy = (top_left_vert.x, top_left_vert.y - 1), text=pronunciation_separated[i], fill=(0,0,0), font = font_type)
            draw.text(xy = (top_left_vert.x, top_left_vert.y + 1), text=pronunciation_separated[i], fill=(0,0,0), font = font_type)
            #Write translated text
            draw.text(xy = (top_left_vert.x, top_left_vert.y), text=pronunciation_separated[i], fill=(255,255,255), font = font_type)
        else:
            #Draw outline of text
            draw.text(xy = (top_left_vert.x - 1, top_left_vert.y), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
            draw.text(xy = (top_left_vert.x + 1, top_left_vert.y), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
            draw.text(xy = (top_left_vert.x, top_left_vert.y - 1), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
            draw.text(xy = (top_left_vert.x, top_left_vert.y + 1), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
            #Write translated text
            draw.text(xy = (top_left_vert.x, top_left_vert.y), text=translated_text_separated[i], fill=(255,255,255), font = font_type)
    return image




# # with open('test.txt', 'w', encoding = 'utf-8') as f:
# #     f.write(str(text_anno.full_text_annotation))
# text_anno = client.text_detection(image=image).text_annotations
# separated_text = text_anno[0].description.split('\n')
# separated_text.pop() #Get rid of last element, which is nothing

# text_index = 1
# #for text in separated_text:

# translated = translator.translate(text_anno[0].description, src = text_anno[0].locale, dest = dest_lang)
# print(translated.pronunciation)
# translated_text_separated = translated.text.split('\n')
# image = Image.open(file_name)
# draw = ImageDraw.Draw(image)
# #print(translated_text_separated)
# for i in range(len(separated_text)):
#     #Get the number of words
#     text_num_words = len(separated_text[i].split(' '))
#     #print(text_num_words)

#     #Get the verticies of the first and last word of the portion being translated
#     verts_first_word = text_anno[text_index].bounding_poly.vertices[0]
#     verts_last_word = text_anno[text_index + text_num_words - 1].bounding_poly.vertices[2]
#     verts_first_word, verts_last_word = check_coords(verts_first_word, verts_last_word)
#     #Crop and blur portion that's being translated
#     cropped_img = image.crop((verts_first_word.x,verts_first_word.y,verts_last_word.x,verts_last_word.y))
#     blurred_img = cropped_img.filter(ImageFilter.GaussianBlur(radius=8))
#     image.paste(blurred_img, (verts_first_word.x,verts_first_word.y))

#     #Set font size to the size of original text
#     font_type = ImageFont.truetype('fonts/times.ttf', verts_last_word.y - verts_first_word.y + 1)
#     #Draw outline of text
#     draw.text(xy = (verts_first_word.x - 1, verts_first_word.y), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
#     draw.text(xy = (verts_first_word.x + 1, verts_first_word.y), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
#     draw.text(xy = (verts_first_word.x, verts_first_word.y - 1), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
#     draw.text(xy = (verts_first_word.x, verts_first_word.y + 1), text=translated_text_separated[i], fill=(0,0,0), font = font_type)
#     #Write translated text
#     draw.text(xy = (verts_first_word.x, verts_first_word.y), text=translated_text_separated[i], fill=(255,255,255), font = font_type)

#     text_index += text_num_words

# print("Finished")
# image.show()