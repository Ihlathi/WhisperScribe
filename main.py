import music_stream as music
import process_OCR as ocr
import sentiment_analysis as analyze
import preprocess_image as preprocess
import get_book_content as book
import threading
import time
import os

READING_SPEED_WPM = 200
WORDS_PER_SPREAD = 600
OCR_INTERVAL = 5
CONTEXT_WINDOW_SIZE = 2000
CONTEXT_WINDOW_THRESHOLD = 200

last_ocr_location = 0
last_image_time = time.time()
curr_reading_loc_word_index = 0
last_check_time = time.time() - 5
current_window_start = 0
current_window_end = 0
scheduled_music_changes = []
position_lock = threading.Lock()

with open("current_reading_session.txt", "w", encoding="utf-8") as f:
    f.write("")
    print("quizfile cleared")

def track_reading_pos():
    global last_ocr_location, last_image_time, curr_reading_loc_word_index, last_check_time
    while True:
        current_time = time.time()

        if current_time - last_check_time >= OCR_INTERVAL:
            image_mtime = os.path.getmtime("image.jpg")
            preprocess.preprocess_image("image.jpg")
            ocr_text = ocr.get_image_text("processed_image.jpg")
            with position_lock:
                if ocr_text:
                    new_location = book.get_index(ocr_text, curr_reading_loc_word_index)
                    
                    if new_location > last_ocr_location + WORDS_PER_SPREAD - 100:
                        last_ocr_location = new_location
                        last_image_time = image_mtime
                        print("got last ocr location")
                else:
                    last_ocr_location += WORDS_PER_SPREAD
                    print("appended to last ocr location")

            last_check_time = current_time
        with position_lock:
            elapsed_seconds = current_time - last_image_time
            estimated_words = (READING_SPEED_WPM / 60) * elapsed_seconds
            curr_reading_loc_word_index = int(last_ocr_location + estimated_words)
            print(f"current estimated reading position: {curr_reading_loc_word_index}")

        time.sleep(0.1)

def schedule_play_music():
    global current_window_start, current_window_end, scheduled_music_changes

    music.start_music()

    while True:
        with position_lock:
            curr_pos = curr_reading_loc_word_index

        if current_window_end == 0 or curr_pos >= current_window_end - CONTEXT_WINDOW_THRESHOLD:
            context = book.get_context(curr_pos, CONTEXT_WINDOW_SIZE)

            print(curr_pos)
            print("got new context" + context)

            with position_lock:
                current_window_start = curr_pos
                current_window_end = curr_pos + CONTEXT_WINDOW_SIZE

            with open("current_reading_session.txt", "a", encoding="utf-8") as file:
                file.write(context + "\n")
                print("wrote context to quizfile")

            with position_lock:
                sentiment_data = analyze.analyse_text(context, curr_reading_loc_word_index)
                print("getting sentiments")
                scheduled_music_changes.clear()
                scheduled_music_changes.append((0, "neutral", 5))

            for entry in sentiment_data:
                trigger_pos, _, sentiment, intensity = entry
                scheduled_music_changes.append((trigger_pos, sentiment, intensity))

        for change in scheduled_music_changes[:]:
            position, sentiment, intensity = change

            if curr_pos >= position:
                music.change(sentiment, intensity)
                scheduled_music_changes.remove(change)

        time.sleep(1)

position_thread = threading.Thread(target=track_reading_pos, daemon=True)
position_thread.start()

print("wait for first ocr to stabilise because no breaky please")
while True:
    with position_lock:
        if curr_reading_loc_word_index > 20:
            time.sleep(5)
            break

    time.sleep(5)

music_thread = threading.Thread(target=schedule_play_music, daemon=True)
music_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("off")