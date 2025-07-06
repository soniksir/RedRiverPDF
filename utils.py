import os

def parse_page_input(page_input, total_pages):
    pages = set()
    try:
        parts = page_input.split(",")
        for part in parts:
            if "-" in part:
                start, end = map(int, part.split("-"))
                if start > end:
                    start, end = end, start
                pages.update(range(start, end + 1))
            else:
                pages.add(int(part))
        valid_pages = [p for p in pages if 1 <= p <= total_pages]
        return sorted(valid_pages)
    except:
        return None

def get_unique_filename(path):
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{base} ({counter}){ext}"
        counter += 1
    return path