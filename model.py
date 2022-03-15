from surprise import SVDpp
from surprise import Dataset, Reader
from typing import List, Tuple, Dict, Iterable, Iterator
import pandas as pd
import pickle
import os
import time
from datetime import datetime

def read_dataset(data_path: str) -> Iterator[Tuple[datetime, int, str, float]]:
    """
    Given a path to a dataset, return a generator that yields tuples
    (time, user_id, movie_id_str, similarity_score) from that dataset.
    """
    with open(data_path, 'r') as f:
        for line in f.readlines():
            time_str, user_id_str, movie_id_str, similarity_str = line.split(',')
            time = datetime.fromisoformat(time_str)
            user_id = int(user_id_str)
            similarity = float(similarity_str)
            yield time, user_id, movie_id_str, similarity


def create_movie_id_mappings_from_file(filename: str, create_pickle: bool=True) -> Tuple[Dict[int, str], Dict[str, int]]:
    """
    Given a filename, create a id for each moviename in the file and
    generate maps to and from that id.
    Preserves the order that the movie ids are given in the file.
    If create_pkl is true, then we additionally generate a pickle file
    with the given mappings.
    """
    movie_names = []
    for _, _, movie_name, _ in read_dataset(filename):
        movie_names.append(movie_name)
    movie_id_to_name, movie_name_to_id = create_movie_id_mappings(movie_names)
    if create_pickle:
        rootname, file_extension = os.path.splitext(filename)
        with open(rootname + '_movie_id_mappings.pkl', 'wb') as f:
            pickle.dump([movie_id_to_name, movie_name_to_id], f)
    return movie_id_to_name, movie_name_to_id


def create_movie_id_mappings(movie_ids: Iterable[str]) -> Tuple[Dict[int, str], Dict[str, int]]:
    """
    Create mappings from movie names to movie ids and back.
    Preserves the order that the movie ids are given in.
    """
    movie_name_to_id : Dict[str, int] = dict()
    movie_id_to_name : Dict[int, str] = dict()
    # unlike set(), dict is guaranteed to preserve
    # insertion order in python3.7+
    unique_movie_names = list(dict.fromkeys(movie_ids)) 
    for id, movie in enumerate(unique_movie_names):
        movie_id_to_name[id] = movie
        movie_name_to_id[movie] = id
    return movie_id_to_name, movie_name_to_id

def create_dataset_from_file_with_mapping(data_path: str,
        movie_name_to_id: Dict[str, int]) -> List[Tuple[int, int, float]]:
    """
    Transform file contents into a representation
    of a dataset (user_id, movie_id, similarity) so as to be
    consistent with the given mapping.
    If a movie is found whose name is not in the map, it will recieve a movie id of len(movie_name_to_id)
    (If needed, we can edit this to increase the size of the movie_name_to_id and
    update a new movie_id_to_name parameter,
    but I can only see this part of the method used for hidden validation data so there's no point.)
    """
    dataset = []
    for _, user_id, movie_id_str, similarity in read_dataset(data_path):
        try:
            dataset.append((user_id, movie_name_to_id[movie_id_str], similarity))
        except KeyError:
            dataset.append((user_id, len(movie_name_to_id), similarity))
    return dataset

class Surprise_Algo():
    def __init__(self, num_recommendations: int = 10):
        self.reader = Reader(rating_scale=(0, 1))
        self.model = SVDpp()
        self.num_recommendations = num_recommendations

    def build_features(self, train_data):
        train_data = pd.DataFrame(train_data, columns=['user_id', 'movie_id', 'rating'])
        features = Dataset.load_from_df(train_data[['user_id', 'movie_id', 'rating']], self.reader)
        return features

    def train(self, correspondences: List[Tuple[int, int, float]], save_path=None) -> None:
        """
        Train the model on the provided correspondences.
        Each correspondence is of the form
        user_id, movie_id, similarity_score
        and it indicates how correlated a user and movie
        are - higher values mean the user likes the movie
        more.
        """
        features = self.build_features(correspondences)
        self.model.fit(features.build_full_trainset())

        if save_path is not None:
            with open(save_path, 'wb') as f:
                pickle.dump(self, f)

    def get_recommendations(self, user_id: int) -> List[int]:
        """
        Very very inefficient: O(Mlog M) where M is the number of known movie IDs,
        the constant factor is big too because of self.model.predict being called in
        a for loop (probablly a matrix multiplication inside)
        """
        all_known_movies = self.model.trainset._raw2inner_id_items.keys()
        my_recs = []
        for movie_id in all_known_movies:
            my_recs.append((movie_id, self.model.predict(uid=user_id, iid=movie_id).est))

        preds_df = pd.DataFrame(my_recs, columns=['movie_id', 'predictions']).\
            sort_values('predictions', ascending=False).head(self.num_recommendations)

        recommendation_ids = preds_df['movie_id'].tolist()
        return recommendation_ids

    def get_similarity(self, user_id: int, movie_id: int) -> float:
        return self.model.predict(uid=user_id, iid=movie_id).est

def make_model(train_path):
    movie_id_to_name, movie_name_to_id = create_movie_id_mappings_from_file(train_path)
    train_data = create_dataset_from_file_with_mapping(train_path, movie_name_to_id)
    baseline = Surprise_Algo(num_recommendations=20)
    baseline.train(train_data)
    return baseline, movie_name_to_id
    

if __name__ == "__main__":
    train_path = 'dataset_partition.csv'
    movie_id_to_name, movie_name_to_id = create_movie_id_mappings_from_file(train_path)
    train_data = create_dataset_from_file_with_mapping(
        train_path, movie_name_to_id)
    baseline = Surprise_Algo(num_recommendations=20)
    start_train_time = time.perf_counter()
    baseline.train(train_data)
    train_time = time.perf_counter() - start_train_time
    print("model train time: {}".format(train_time))
    recommendation_ids = baseline.get_recommendations(123)
    recommendation_ids = baseline.get_recommendations(9999999999)
    print(recommendation_ids)
    movies = []
    for item in recommendation_ids:
        movies.append(movie_id_to_name[item])
    print(movies)
    print(baseline.get_similarity(567781,129))