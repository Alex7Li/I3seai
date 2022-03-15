# Evaluate Performace of System

import aporia
from consumer_factory import create_consumer
from datetime import datetime

aporia.init(token="bcfdab4e222d1de5b441c793b0e415bc92a7e78c2bdf82b9dd104e03e2868f74", 
            environment="local-dev", 
            verbose=True)
def aporia_setup_timelogger():
    """
    Setup a schema in aporia to view the model.
    """
    apr_model_version = "system_perf_v1"
    apr_model_type = "regression"
    apr_features_schema = {
        # "created_at": "datetime",
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
apr_model = aporia_setup_timelogger()

for message in create_consumer():
    data = list(map(str.strip,message.value.decode().split(',')))

    apr_prediction_id = data[0] + data[1]


    # apr_features_dict = None
    # apr_prediction_dict = None
    
    # if data[-1].startswith('GET /rate/'):
        
    #     in_time = datetime.fromisoformat(data[0])
    #     user_id = int(data[1])
        
    #     apr_prediction_id = data[0] + data[1]

    #     apr_features_dict = {
    #         "created_at": in_time, #datetime.fromisoformat('2022-03-01T17:22:37')
    #         "user_id": user_id,
    #     }
        

    if data[2].startswith('recommendation request'):
        
        response_time = int(data[-1][:-3]) #in milliseconds
        user_id = int(data[1])

        apr_features_dict = {
            "user_id": user_id,
        }
        
        apr_prediction_dict = {
            'response_time': response_time,
        }

        apr_model.log_prediction(
            id=apr_prediction_id,
            features=apr_features_dict,
            predictions=apr_prediction_dict,
        )
    
        apr_model.flush()
