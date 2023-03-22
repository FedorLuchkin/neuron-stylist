import path_editor
import re

frequency = {}

document_text = open('sessions.log', 'r')
text_string = document_text.read().lower()

text_string = re.sub("DEBUG", "DEBUG ", text_string)
text_string = re.sub("INFO", "INFO ", text_string)
text_string = re.sub("ERROR", "ERROR ", text_string)
matches = re.findall(r'\b[a-z]{3,15}\b', text_string)

for word in matches:
    count = frequency.get(word,0)
    frequency[word] = count + 1

for el in ("debug", "info", "error"):
    if el in frequency.keys():
        print(f"{el}: {frequency[el]}")
    else:
        print(f"{el}: 0")
