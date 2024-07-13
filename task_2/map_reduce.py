import argparse
import string
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
import requests


def get_text(url_):
    try:
        response = requests.get(url_, verify=False)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text):
    text = remove_punctuation(text)
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(words_map, top=10):
    top_words = dict(sorted(words_map.items(), key=lambda item: item[1], reverse=True)[:top])

    _, ax = plt.subplots()

    words = top_words.keys()
    frequency = top_words.values()

    y_pos = np.arange(top)
    ax.barh(y_pos, frequency, color='c', align='center')
    ax.set_yticks(y_pos, labels=words)
    ax.invert_yaxis()
    ax.set_ylabel('Words')
    ax.set_xlabel('Frequency')
    ax.set_title(f'Top {top} Most Frequent words')

    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url')
    parser.add_argument('-t', '--top', type=int, default=10)
    args = parser.parse_args()

    url, top = args.url, args.top

    text = get_text(url)

    if text:
        result = map_reduce(text)
        visualize_top_words(result, top)
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")
