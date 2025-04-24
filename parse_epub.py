from ebooklib import epub
from bs4 import BeautifulSoup

def extract_epub_text(file_path):
    book = epub.read_epub(file_path)
    text_segments = []

    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            text_segments.append(text)

    return text_segments

if __name__ == "__main__":
    epub_path = input("Enter the path to the EPUB file: ")
    segments = extract_epub_text(epub_path)
    book = ""
    for segment in segments:
        print(segment)
        book += segment

        with open ("book.txt", 'w', encoding="utf_8") as file:
            file.write(book)
