
import PyPDF2
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path
# Для выполнения OCR, чтобы извлекать тексты из изображений
import pytesseract
# Для удаления дополнительно созданных файлов
import os


# Создаём функцию для вырезания элементов изображений из PDF
def crop_image(element, pageObj):
    # Получаем координаты для вырезания изображения из PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1]
    # Обрезаем страницу по координатам (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Сохраняем обрезанную страницу в новый PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Сохраняем обрезанный PDF в новый файл
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# Создаём функцию для преобразования PDF в изображения
def convert_to_images(input_file,):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")

# Создаём функцию для считывания текста из изображений
def image_to_text(image_path):
    # Считываем изображение
    img = Image.open(image_path)
    # Извлекаем текст из изображения
    text = pytesseract.image_to_string(img)
    return text

def text_extraction(element):
    # Извлекаем текст из вложенного текстового элемента
    line_text = element.get_text()
    # Находим форматы текста
    # Инициализируем список со всеми форматами, встречающимися в строке текста
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Итеративно обходим каждый символ в строке текста
            for character in text_line:
                if isinstance(character, LTChar):
                    # Добавляем к символу название шрифта
                    line_formats.append(character.fontname)
                    # Добавляем к символу размер шрифта
                    line_formats.append(character.size)
    # Находим уникальные размеры и названия шрифтов в строке
    format_per_line = list(set(line_formats))

    # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
    return (line_text, format_per_line)




def get_pdf_text(pdf_path):
    for pagenum, page in enumerate(extract_pages(pdf_path)):
    # Итеративно обходим элементы, из которых состоит страница
        for element in page:
            # Проверяем, является ли элемент текстовым
            if isinstance(element, LTTextContainer):
                # Функция для извлечения текста из текстового блока
                pass
                # Функция для извлечения формата текста
                pass

            # Проверка элементов на наличие изображений
            if isinstance(element, LTFigure):
                # Функция для преобразования PDF в изображение
                pass
                # Функция для извлечения текста при помощи OCR
                pass

            # Проверка элементов на наличие таблиц
            if isinstance(element, LTRect):
                # Функция для извлечения таблицы
                pass
                # Функция для преобразования содержимого таблицы в строку
                pass















# import pdfplumber
#
#
# def get_pdf_text():
#     with pdfplumber.open("Docs/bazi_dannih.pdf") as pdf:
#         text = ""
#         for page in pdf.pages:
#             text += page.extract_text().replace("-\n", "")
#         paragraphs = text.split("\n\n")
#
#         fragments = [p.strip() for p in paragraphs if p.strip()]
#     return fragments