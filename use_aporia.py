# Evaluate Performace of System

import aporia
from consumer_factory import create_consumer
# from datetime import datetime
import numpy as np

aporia.init(token="bcfdab4e222d1de5b441c793b0e415bc92a7e78c2bdf82b9dd104e03e2868f74", 
            environment="local-dev", 
            verbose=True)

def aporia_setup_timelogger():
    """
    Setup a schema in aporia to view the model.
    """
    apr_model_version = "system_perf_v2"
    apr_model_type = "regression"
    apr_features_schema = {
        # "created_at": "datetime",
        "user_id": "string",
    }
    apr_predictions_schema = {
        'response_time': 'numeric',
        'response_time_moving_average': 'numeric',
    }

    return aporia.create_model_version(
        model_id="movie-recommendation",
        model_version=apr_model_version,
        model_type=apr_model_type,
        features=apr_features_schema,
        predictions=apr_predictions_schema
    )
apr_model = aporia_setup_timelogger()

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

response_time_arr = []
threshold = 10


for message in create_consumer():
    data = list(map(str.strip,message.value.decode().split(',')))

    apr_prediction_id = data[0] + data[1]
    
    

    

    if data[2].startswith('recommendation request'):
        
        response_time = int(data[-1].split()[0]) #in milliseconds

        response_time_arr.append(response_time)
        
        if len(response_time_arr) == threshold:
            # print(f"response time:")
            response_time_moving_average = moving_average(response_time_arr,threshold)[0]
            print(f"response time moving average: {response_time_moving_average} ms")
            response_time_arr = response_time_arr[1:]
            
            user_id = data[1]

            apr_features_dict = {
                "user_id": user_id,
            }
            
            apr_prediction_dict = {
                'response_time': response_time,
                'response_time_moving_average': response_time_moving_average
            }

            apr_model.log_prediction(
                id=apr_prediction_id,
                features=apr_features_dict,
                predictions=apr_prediction_dict,
            )
        
            apr_model.flush()
