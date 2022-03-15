import itertools
from tqdm import tqdm

from consumer_factory import create_consumer
def get_data(n_entries=100):
    consumer = create_consumer()
    data = []
    for message in tqdm(itertools.islice(consumer, n_entries)):
        data.append(message.value)
    return data

if __name__ == '__main__':
    get_data(10)