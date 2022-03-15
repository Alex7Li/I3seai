import aporia

aporia.init(token="bcfdab4e222d1de5b441c793b0e415bc92a7e78c2bdf82b9dd104e03e2868f74", 
            environment="local-dev", 
            verbose=True)
def aporia_setup_timelogger():
    """
    Setup a schema in aporia to view the model.
    """
    apr_model_version = "sandbox-version2"
    apr_model_type = "ranking"
    apr_features_schema = {
        "created_at": "datetime",
        "user_id": "numeric",
    }
    apr_predictions_schema = {
        'response_time': 'numeric'
    }

    return aporia.create_model_version(
        model_id="movie-recommendation",
        model_version=apr_model_version,
        model_type=apr_model_type,
        features=apr_features_schema,
        predictions=apr_predictions_schema
    )

def aporia_setup_ratinglogger():
    """
    Setup a schema in aporia to view the model.
    """
    aporia.init(token="bcfdab4e222d1de5b441c793b0e415bc92a7e78c2bdf82b9dd104e03e2868f74", 
                environment="local-dev", 
                verbose=True)
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
apr_model = aporia_setup()

apr_prediction_id = "pred_1337"

apr_features_dict = {
    "amount": 3918,
    "owner": "John Doe",
    "is_new": "true",
    "created_at": "2021-01-17",
}

apr_prediction_dict = {
    "approved": "true",
    "confidence": 0.81,
}

apr_model.log_prediction(
    id=apr_prediction_id,
    features=apr_features_dict,
    predictions=apr_prediction_dict,
)

apr_model.flush()
