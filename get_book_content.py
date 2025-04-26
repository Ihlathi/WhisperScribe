from rapidfuzz import fuzz
import re

def get_index(snippet):
    match_window_index = None
    match_index = None
    top_score = 0
    print("finding location")

    step = 400
    text_window = 500

    fine_step = 1
    fine_window = len(snippet)

    with open ("book.txt", 'r', encoding='utf_8') as file:
        book_text = file.read()

    for i in range(0, len(book_text) - text_window, step):
        book_text_chunk = book_text[i:i + text_window]
        score = fuzz.partial_ratio(snippet, book_text_chunk)

        if score > top_score:
            top_score = score
            match_window_index = i

    if match_window_index is not None:
        top_score = 0
        best_chunk = book_text[match_window_index:match_window_index + text_window]

        for i in range(0, len(best_chunk) - fine_window, fine_step):
            best_chunk_chunk = best_chunk[i:i + fine_window]
            score = fuzz.partial_ratio(snippet, best_chunk_chunk)

            if score > top_score:
                top_score = score
                match_index = i

        if match_index is not None:
            match_index = match_window_index + match_index
        else: 
            match_index = match_window_index

    book_in_words = re.findall(r'\S+', book_text)
    print(len(book_in_words))

    curr_index = 0
    start_word_index = 0

    for i, word in enumerate(book_in_words):
        curr_index = book_text.find(word, curr_index)

        if curr_index >= match_index:
            start_word_index = i
            break
        
        curr_index += len(word)

    return start_word_index

def get_context(word_index, context_size):
    print("getting context")

    with open ("book.txt", 'r', encoding='utf_8') as file:
        book_text = file.read()

    book_in_words = re.findall(r'\S+', book_text)
    print(len(book_in_words))

    curr_index = 0
    start_word_index = 0

    for i, word in enumerate(book_in_words):
        curr_index = book_text.find(word, curr_index)

        if curr_index >= word_index:
            start_word_index = i
            break
        
        curr_index += len(word)

    context_start = max(start_word_index, 0)
    context_end = min(start_word_index + context_size, len(book_in_words))

    context_split_words = book_in_words[context_start:context_end]
    context = ' '.join(context_split_words)
    return context


if __name__ == "__main__":
    # print("hi")
    # index = find_location("i can't tell where athena ends")
    # print(index)
    get_context("exquisitely literary,", 600)