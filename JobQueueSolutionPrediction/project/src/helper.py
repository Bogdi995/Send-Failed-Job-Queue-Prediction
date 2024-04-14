import sys
import spacy
import numpy as np
from typing import Callable
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

sys.path.append('src')

from src.model_training import ModelTraining
from src.text_preprocessing import TextPreprocessing
from src.named_entity_recognition import NamedEntityRecognition


class Helper:

    def __init__(self):
        self.confidence: float
        self.prediction_array: np.ndarray
        self.prediction: str

    @staticmethod
    def process_job_queue_error(
        job_queue_error: str, 
        trained_nlp: spacy.Language, 
        preprocessing_functions: dict[str, Callable[[str], str]], 
        contractions: dict[str, str],
        config: dict[str, any]
    ) -> str:
        """
        Process the job queue error message by replacing characters, entities, and applying preprocessing.

        Args:
            job_queue_error (str): The job queue error message.
            trained_nlp (spacy.Language): The trained NLP model.
            preprocessing_functions (dict[str, Callable[[str], str]]): A dictionary of preprocessing functions.
            contractions (dict[str, str]): A dictionary of contractions.
            config (dict[str, any]): The configuration file.

        Returns:
            str: The preprocessed job queue error message.
        """
        job_queue_error = job_queue_error.replace("=", " ").replace("'", " ")
        job_queue_error = NamedEntityRecognition.replace_entities([job_queue_error], trained_nlp)[0]
        preprocessed_job_queue_error = TextPreprocessing.preprocess_utterance(job_queue_error, preprocessing_functions, contractions, config)
        
        return preprocessed_job_queue_error

    def calculate_prediction(
        self,
        preprocessed_job_queue_error: str,
        intents: dict[str, list[str]],
        vectorizer: dict[dict[str, object], list[str]],
        job_queue_label_encoder: LabelEncoder,
        job_queue_model: tf.keras.models.Sequential
    ) -> None:
        """
        Print the prediction result for a preprocessed job queue error.

        Args:
            preprocessed_job_queue_error (str): The preprocessed job queue error.
            intents (dict[str, list[str]]): A dictionary containing intents and responses.
            vectorizer (dict[dict[str, object], list[str]]): A dictionary containing the vectorizer configuration.
            job_queue_label_encoder (LabelEncoder): The label encoder for job queue errors.
            job_queue_model (tf.keras.models.Sequential): The trained Sequential model for job queue errors.

        Returns:
            None
        """
        np.set_printoptions(suppress = True)

        vectorized_preprocessed_job_queue_error = ModelTraining.vectorize_text(preprocessed_job_queue_error, vectorizer)
        self.prediction_array = job_queue_model.predict(vectorized_preprocessed_job_queue_error)
        prediction_index: int = np.argmax(self.prediction_array)
        tag: np.ndarray = job_queue_label_encoder.inverse_transform([prediction_index])
        self.confidence = np.amax(self.prediction_array)

        for i in intents["intents"]:
            if i["tag"] == tag:
                self.prediction = i["response"]