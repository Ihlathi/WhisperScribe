from rapidfuzz import fuzz
import re

with open("book.txt", "r", encoding="utf-8") as file:
    book_text = file.read()
book_in_words = re.findall(r'\S+', book_text)
book_text_words = " ".join(book_in_words).lower()

def get_index(snippet, hint_position=None):
    match_window_index = None
    match_index = None
    top_score = 0
    print("finding location")

    snippet = snippet.lower()
    snippet_words = re.findall(r'\S+', snippet)

    snippet_text = " ".join(snippet_words)
    snippet_len = len(snippet_words)

    step = max(1, snippet_len)
    text_window = max(3, snippet_len * 3)

    for i in range(0, len(book_in_words) - text_window + 1, step):
        window = book_in_words[i:i + text_window]
        book_text_chunk = " ".join(window).lower()
        score = fuzz.partial_ratio(snippet_text, book_text_chunk)

        if hint_position is not None:
            distance_penalty = abs(i - hint_position) / len(book_in_words)
            score *= (1 - 0.5 * distance_penalty)

        if score > top_score:
            top_score = score
            match_window_index = i

    if match_window_index is not None:
        top_score = 0
        best_chunk = book_in_words[match_window_index:match_window_index + text_window]

        fine_step = 1
        fine_window = len(snippet_words)
        for i in range(0, len(best_chunk) - fine_window, fine_step):
            best_chunk_chunk = " ".join(best_chunk[i:i + fine_window])
            score = fuzz.partial_ratio(snippet_text, best_chunk_chunk)

            if score > top_score:
                top_score = score
                match_index = i

        if match_index is not None:
            match_index = match_window_index + match_index
        else:
            match_index = match_window_index

    return match_index if match_index is not None else 0

def get_context(word_index, context_size):
    print("getting context")
    print(len(book_in_words))

    context_start = max(word_index, 0)
    context_end = min(word_index + context_size, len(book_in_words))

    context_split_words = book_in_words[context_start:context_end]
    context = ' '.join(context_split_words)
    return context