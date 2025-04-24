from rapidfuzz import process, fuzz
import re

def find_location(ocr_snippet):
    best_match = None
    top_score = 0
    print("finding location")

    step = 50
    text_window = 500

    with open ("book.txt", 'r', encoding='utf_8') as file:
        book_text = file.read()

    for i in range(0, len(book_text) - text_window, step):
        book_text_chunk = book_text[i:i + text_window]
        identified_score = fuzz.partial_ratio(ocr_snippet, book_text_chunk)

        if identified_score > top_score:
            top_score = identified_score
            best_match = i

    return best_match

def get_context(best_match):
    with open ("book.txt", 'r', encoding='utf_8') as file:
        book_text = file.read()

    book_in_words = re.findall(r'\S+', book_text)
    print(len(book_in_words))

    curr_index = 0
    best_match_word_index = 0

    for i, word in enumerate(book_in_words):
        curr_index = book_text.find(word, curr_index)

        if curr_index >= best_match:
            best_match_word_index = i
            break
        
        curr_index += len(word)

    context_start = max(best_match_word_index - 100, 0)
    context_end = min(best_match_word_index + 500, len(book_in_words))

    context_split_words = book_in_words[context_start:context_end]
    context = ' '.join(context_split_words)
    print(context)


if __name__ == "__main__":
    print("hi")
    index = find_location("i can't tell where athena ends")
    print(index)
    get_context(index)