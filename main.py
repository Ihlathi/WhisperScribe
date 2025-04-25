import music_stream as music
import process_OCR as ocr
import sentiment_analysis as analyze
import get_book_content as book

READING_SPEED_WPM = 200
WORDS_PER_SPREAD = 600

OCR_location = 0



def do_thing():
    ocr_text = ocr.get_image_text("image.jpg")

    if ocr_text != []:
        OCR_location = book.find_location(ocr_text)
    else:
        OCR_location += WORDS_PER_SPREAD
    
    book.get_context