import music_stream as music
import process_OCR as ocr
import sentiment_analysis as analyze
import preprocess_image as preprocess
import get_book_content as book
import threading
import time
import os

# constants
READING_SPEED_WPM = 200
WORDS_PER_SPREAD = 600
OCR_INTERVAL = 2.5
CONTEXT_WINDOW_SIZE = 2000
CONTEXT_WINDOW_THRESHOLD = 200

# global vars
last_ocr_location = None
last_image_time = None
curr_reading_loc_word_index = None
last_check_time = None
current_window_start = None
current_window_end = None
scheduled_music_changes = []  # list of (position, sentiment, intensity)
position_lock = threading.Lock()

# clear quiz file
with open("current_reading_session.txt", "w", encoding="utf-8") as f:
    f.write("")


def track_reading_pos():
    global last_ocr_location, last_image_time, curr_reading_loc_word_index, last_check_time

    while True:
        current_time = time.time()

        if current_time - last_check_time >= OCR_INTERVAL:
            last_image_time = os.path.getmtime("image.jpg")

            preprocess.preprocess_image("image.jpg")
            ocr_text = ocr.get_image_text("processed_image.jpg")

            with position_lock:
                if ocr_text:
                    last_ocr_location = book.get_index(ocr_text)
                else:
                    last_ocr_location += WORDS_PER_SPREAD

            last_check_time = current_time # update time of last check

        with position_lock:
            elapsed_seconds = current_time - last_image_time # how long since image was sent
            estimated_words = (READING_SPEED_WPM / 60) * elapsed_seconds
            curr_reading_loc_word_index = int(last_ocr_location + estimated_words)
            print(f"Current position: {curr_reading_loc_word_index}")
        time.sleep(0.1)

def schedule_play_music():
    global current_window_start, current_window_end, scheduled_music_changes

    first_run = True # start with neutral if program just started

    if first_run == True:
        music.start_music()
        first_run = False

    while True:
        with position_lock:
            curr_pos = curr_reading_loc_word_index
        
        if current_window_end == None or curr_pos >= current_window_end - CONTEXT_WINDOW_THRESHOLD:
            context = book.get_context(curr_pos, CONTEXT_WINDOW_SIZE)
        
        with position_lock:
            current_window_start = curr_pos
            current_window_end = curr_pos + CONTEXT_WINDOW_SIZE

        with open("current_reading_session.txt", "a", encoding="utf-8") as file:
            file.write(context + "\n")
        
        sentiment_data = analyze.analyse_text(context)

        for entry in sentiment_data:
            trigger_phrase, sentiment, intensity = entry

            trigger_pos = book.get_index(trigger_phrase)

            scheduled_music_changes.append((trigger_pos, sentiment, intensity))

        for change in scheduled_music_changes[:]:
            position, sentiment, intensity = change

            if curr_pos >= position:
                music.change(sentiment, intensity)
                scheduled_music_changes.remove(change)

            time.sleep(1)



position_thread = threading.Thread(target=track_reading_pos, daemon=True)
music_thread = threading.Thread(target=schedule_play_music, daemon=True)
position_thread.start()
music_thread.start()
position_thread.join()
music_thread.join()