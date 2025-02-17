import requests
import string
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import asyncio
import time

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

def map_processing(lines, num_threads=8):
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        map_results = list(executor.map(map_word_count, lines))
    return map_results

async def async_map_processing(lines, num_threads=8):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        tasks = [loop.run_in_executor(executor, map_word_count, line) for line in lines]
        map_results = await asyncio.gather(*tasks)
    return map_results

def visualize_timings(sync_time, async_time):
    labels = ['Sync', 'Async']
    times = [sync_time, async_time]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, times, color=['coral', 'lightgreen'])
    plt.ylabel('Час (секунди)')
    plt.title('Порівняння часу обробки Map')
    for i, t in enumerate(times):
        plt.text(i, t, f"{t:.4f}s", ha='center', va='bottom')
    plt.show()

if __name__ == '__main__':
    url = "https://www.gutenberg.org/cache/epub/17989/pg17989.txt"
    response = requests.get(url)
    print("Завантажено текст із URL")
    text_data = response.text
    lines = text_data.split('\n')
    print("Текст поділено на рядки")
    num_threads = 8

    start = time.perf_counter()
    sync_map_results = map_processing(lines, num_threads)
    sync_time = time.perf_counter() - start
    print(f"Синхронна обробка Map завершена за {sync_time:.4f} секунд")

    start = time.perf_counter()
    async_map_results = asyncio.run(async_map_processing(lines, num_threads))
    async_time = time.perf_counter() - start
    print(f"Асинхронна обробка Map завершена за {async_time:.4f} секунд")

    if sync_map_results == async_map_results:
        print("Результати синхронної та асинхронної обробки Map однакові.")
    else:
        print("Розбіжності в результатах обробки Map!")

    sync_word_counts = reduce_word_counts(sync_map_results)
    async_word_counts = reduce_word_counts(async_map_results)
    if sync_word_counts == async_word_counts:
        print("Результати редукції для обох методів однакові.")
    else:
        print("Результати редукції відрізняються!")

    visualize_top_words(sync_word_counts, top_n=10)
    visualize_timings(sync_time, async_time)
