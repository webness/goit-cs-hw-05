import requests
import string
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

def map_word_count(text_chunk):
    text_chunk = text_chunk.lower()
    text_chunk = text_chunk.translate(str.maketrans('', '', string.punctuation))
    words = text_chunk.split()
    word_dict = {}
    for word in words:
        if len(word) < 4:
            continue
        if word not in word_dict:
            word_dict[word] = 0
        word_dict[word] += 1
    return word_dict

def reduce_word_counts(dict_list):
    final_dict = {}
    for d in dict_list:
        for word, count in d.items():
            if word not in final_dict:
                final_dict[word] = 0
            final_dict[word] += count
    return final_dict

def visualize_top_words(word_counts, top_n=10):
    sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_words = sorted_counts[:top_n]
    words = [item[0] for item in top_words]
    counts = [item[1] for item in top_words]
    plt.figure(figsize=(8, 5))
    plt.barh(words, counts, color='skyblue')
    plt.xlabel('Частота')
    plt.ylabel('Слова')
    plt.title(f'Топ {top_n} найчастіших слів')
    plt.gca().invert_yaxis()
    print("Візуалізацію завершено. Відображаємо діаграму найпоширеніших слів...")
    plt.show()

if __name__ == '__main__':
    url = "https://www.gutenberg.org/cache/epub/17989/pg17989.txt"
    response = requests.get(url)
    print("Завантажено текст із URL")
    text_data = response.text
    lines = text_data.split('\n')
    print("Текст поділено на рядки")
    num_threads = 8
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        map_results = list(executor.map(map_word_count, lines))
    print("Завершено крок Map. Кількість часткових результатів:", len(map_results))
    word_counts = reduce_word_counts(map_results)
    print("Завершено крок Reduce. Унікальних слів:", len(word_counts))
    visualize_top_words(word_counts, top_n=10)
