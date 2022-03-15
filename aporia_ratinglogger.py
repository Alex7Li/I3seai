import aporia
from eat_kafka import get_data
import model
from datetime import datetime
from consumer_factory import create_consumer

aporia.init(token="bcfdab4e222d1de5b441c793b0e415bc92a7e78c2bdf82b9dd104e03e2868f74", 
            environment="local-dev", 
            verbose=True)
def aporia_setup_ratinglogger():
    """
    Setup a schema in aporia to view the model.
    """
    apr_model_version = "sandbox-version2"
    apr_model_type = "ranking"
    apr_features_schema = {
        "created_at": "datetime",
        "user_id": "numeric",
        "movie_name": "categorical",
    }
    apr_predictions_schema = {
        'rating': 'numeric'
    }

    return aporia.create_model_version(
        model_id="movie-recommendation",
        model_version=apr_model_version,
        model_type=apr_model_type,
        features=apr_features_schema,
        predictions=apr_predictions_schema
    )
apr_model = aporia_setup_ratinglogger()
rec_model, movie_id_to_model_id = model.make_model('dataset_partition.csv')

for message in create_consumer():
    data = message.value.decode().split(',')
    if data[-1].startswith('GET /rate/'):
        # Format:
        # <time>,<userid>,GET /rate/<movieid>=<rating>
        movie_id, rating_raw = data[-1][10:].split('=')
        true_rating = int(rating_raw)
        print(f'read rating {message.value}')
        apr_prediction_id = data[0] + data[1]
        time = datetime.fromisoformat(data[0])
        user_id = int(data[1])
        apr_features_dict = {
            "created_at": time,
            "user_id": user_id,
            "movie_name": movie_id,
        }
        predicted_rating = rec_model.get_similarity(
            user_id, movie_id_to_model_id[movie_id]
        ) * 4 + 1
        apr_prediction_dict = {
            "rating": predicted_rating,
        }
        apr_actual_dict = {
            "rating": true_rating,
        }

        apr_model.log_prediction(
            id=apr_prediction_id,
            features=apr_features_dict,
            predictions=apr_prediction_dict,
            actual=apr_actual_dict,
        )

        apr_model.flush()
