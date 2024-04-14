import os
import sys
import spacy
import numpy as np
import tensorflow as tf
from typing import Callable
from sklearn.preprocessing import LabelEncoder
from keras.layers import TextVectorization

sys.path.append('src')

from src.data_loading import DataLoading
from src.helper import Helper


def load_data(config: dict[str, any], script_dir: str) -> tuple:
    """
    Load various data needed for prediction.

    Args:
        config (dict[str, any]): Configuration parameters.
        script_dir: str: The script directory path.

    Returns:
        tuple: Tuple containing loaded data.
    """
    intents_path: str = os.path.join(script_dir, config['paths']['intents'])
    trained_nlp_path: str = os.path.join(script_dir, config['paths']['nlp'])
    contractions_path: str = os.path.join(script_dir, config['paths']['contractions'])
    preprocessing_functions_path: str = os.path.join(script_dir, config['paths']['preprocessing_functions'])
    job_queue_vectorizer_path: str = os.path.join(script_dir, config['paths']['vectorizer'])
    job_queue_label_encoder_path: str = os.path.join(script_dir, config['paths']['label_encoder'])
    job_queue_model_path: str = os.path.join(script_dir, config['paths']['model'])
    
    intents: dict[str, list[str]] = DataLoading.load_intents(intents_path)
    trained_nlp: spacy.Language = DataLoading.load_trained_nlp(trained_nlp_path)
    contractions: dict[str, str] = DataLoading.load_contractions(contractions_path)
    preprocessing_functions: dict[str, Callable[[str], str]] = DataLoading.load_preprocessing_functions(preprocessing_functions_path)
    job_queue_vectorizer: dict[dict[str, object], list[str]] = DataLoading.load_job_queue_vectorizer(job_queue_vectorizer_path)
    job_queue_label_encoder: LabelEncoder = DataLoading.load_label_encoder(job_queue_label_encoder_path)
    job_queue_model: tf.keras.models.Sequential = DataLoading.load_keras_model(job_queue_model_path)

    return intents, trained_nlp, contractions, preprocessing_functions, job_queue_vectorizer, job_queue_label_encoder, job_queue_model

def predict_solution(error_message: str) -> tuple[str, float]:
    """
    Predict function to perform prediction.

    Args:
        error_message (str): The error message for prediction.

    Returns:
        tuple[str, float]: A tuple containing the prediction, and confidence.
    """
    script_dir: str = os.path.dirname(os.path.realpath(__file__))
    config_path: str = os.path.join(script_dir, 'config.json')
    config: dict[str, any] = DataLoading.load_config(config_path)
    tf.random.set_seed(42)

    (intents, trained_nlp, contractions, preprocessing_functions, job_queue_vectorizer, 
     job_queue_label_encoder, job_queue_model) = load_data(config, script_dir)

    vectorizer: TextVectorization = TextVectorization.from_config(job_queue_vectorizer["config"])
    vectorizer.set_weights(job_queue_vectorizer["weights"])

    helper = Helper()

    preprocessed_job_queue_error: str = helper.process_job_queue_error(
        error_message, trained_nlp, preprocessing_functions, contractions, config
    )

    helper.calculate_prediction(
        preprocessed_job_queue_error, intents, vectorizer, job_queue_label_encoder, job_queue_model
    )

    return helper.prediction, helper.confidence

if __name__ == "__main__":
    job_queue_error: str = "Die E-Mail-Adresse 'test.bobl@axians-infoma.com' ist ungültig."
    print(predict_solution(job_queue_error))