import dill
import json
import spacy
import pickle
import tensorflow as tf
from typing import Callable
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder


class DataLoading:

    @staticmethod
    def load_config(file_path: str) -> dict[str, any]:
        """
        Load configuration data from a JSON file.

        Args:
            file_path (str): Path to the configuration JSON file.'.

        Returns:
            dict[str, any]: A dictionary containing the configuration data.
        """
        with open(file_path, 'r') as file:
            config_data = json.load(file)
    
        return config_data
    
    @staticmethod
    def load_intents(file_path: str) -> dict[str, list[str]]:
        """
        Loads intents from a JSON file.

        Args:
            file_path (str): The path of the JSON file.

        Returns:
            dict[str, list[str]]: A dictionary containing intents.
        """
        with open(file_path, encoding="utf-8") as file:
            intents: dict[str, list[str]] = json.load(file)
        
        return intents
    
    @staticmethod
    def load_stopwords(file_path: str) -> list[str]:
        """
        Loads stopwords from a text file.

        Args:
            file_path (str): The path of the text file to load.

        Returns:
            list[str]: A list of stopwords loaded from the file.
        """
        stopwords: list[str] = []
        
        with open(file_path, "r") as file:
            for line in file:
                stopwords.append(line.strip())
                
        return stopwords

    @staticmethod
    def load_trained_nlp(file_path: str) -> spacy.Language:
        """
        Loads a trained NLP model.

        Args:
            file_path (str): The path to the file.

        Returns:
            spacy.Language: The loaded nlp object.
        """
        trained_nlp: spacy.Language = spacy.load(file_path)
            
        return trained_nlp


    @staticmethod
    def load_contractions(file_path: str) -> dict[str, str]:
        """
        Loads contractions from a text file and returns them as a dictionary.
        The text file should contain lines with key-value pairs separated by the '=' symbol.
        Each line represents a contraction, where the key is the contraction and the value is the expanded form.
        
        Args:
            file_path (str): The path of the text file to read contractions from.
            
        Returns:
            dict[str, str]: A dictionary containing the loaded contractions.
        """
        contractions = {}

        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split("=")
                contractions[key] = value

        return contractions
    
    @staticmethod
    def load_entities(file_path: str) -> dict[str, list[str]]:
        """
        Loads entities from a text file and returns them as a dictionary.
        The text file should be formatted with section headings followed by items listed under each section.
        Section headings end with a colon (':'), and items start with a hyphen ('-').
        
        Args:
            file_path (str): The path of the text file to read entities from.
            
        Returns:
            dict: A dictionary containing the loaded entities.
        """
        entities: dict[str, list[str]] = {}

        with open(file_path, "r") as file:
            current_key = None

            for line in file:
                line = line.strip()

                if line.endswith(":"):
                    current_key = line[:-1]
                    entities[current_key] = []
                elif line.startswith("-"):
                    value = line[2:]
                    entities[current_key].append(value)

        return entities
    
    # @staticmethod
    # def load_data(file_path: str) -> dict[str, list[str]]:
    #     """
    #     Loads data from a JSON file and returns it as a dictionary.

    #     Args:
    #         file_path (str): The path to the JSON file.

    #     Returns:
    #         dict[str, list[str]]: A dictionary containing lists of training utterances, labels, responses, and unique labels.
    #     """
    #     with open(file_path, encoding ="utf-8") as file:
    #         data: dict[str, list[str]] = json.load(file)
        
    #     return data
    
    @staticmethod
    def load_contractions(file_path: str) -> dict:
        """
        Loads contractions from a text file and returns them as a dictionary.
        The text file should contain lines with key-value pairs separated by the '=' symbol.
        Each line represents a contraction, where the key is the contraction and the value is the expanded form.
        
        Args:
            file_path (str): The path of the text file to read contractions from.
            
        Returns:
            dict: A dictionary containing the loaded contractions.
        """
        contractions = {}

        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split("=")
                contractions[key] = value

        return contractions

    @staticmethod
    def load_preprocessing_functions(file_path: str) -> dict[str, Callable[[str], str]]:
        """
        Loads preprocessing functions from a pickle file.
        
        Args:
            file_path (str): The path to the pickle file containing the preprocessing functions.
        
        Returns:
            dict[str, Callable[[str], str]]: A dictionary mapping function names to preprocessing functions.
                The functions take a string as input and return a processed string as output.
        """
        with open(file_path, "rb") as preprocessing_file:
            preprocessing_functions: dict[str, Callable[[str], str]] = dill.load(preprocessing_file)
        
        return preprocessing_functions

    @staticmethod
    def load_job_queue_vectorizer(file_path: str) -> dict[dict[str, object], list[str]]:
        """
        Loads the job queue vectorizer from a pickle file.
        
        Args:
            file_path (str): The path to the pickle file containing the job queue vectorizer.
        
        Returns:
            dict[dict[str, object], list[str]]: The loaded job queue vectorizer.
                It is represented as a dictionary mapping configuration parameters to a list of vectorized features.
        """
        with open(file_path, "rb") as vectorizer_file:
            job_queue_vectorizer: dict[dict[str, object], list[str]] = pickle.load(vectorizer_file)
        
        return job_queue_vectorizer

    @staticmethod
    def load_vectorized_dataset(file_path: str) -> tf.Tensor:
        """
        Loads the vectorized dataset from a pickle file.
        
        Args:
            file_path (str): The path to the pickle file containing the vectorized dataset.
        
        Returns:
            tf.Tensor: The loaded vectorized dataset.
        """
        with open(file_path, "rb") as vectorized_dataset_file:
            vectorized_dataset: tf.Tensor = pickle.load(vectorized_dataset_file)

        return vectorized_dataset

    @staticmethod
    def load_label_encoder(file_path: str) -> LabelEncoder:
        """
        Load a LabelEncoder object from a pickle file.

        Args:
            file_path (str): The path to the pickle file to load the LabelEncoder from.

        Returns:
            LabelEncoder: The loaded LabelEncoder object.
        """
        with open(file_path, "rb") as label_encoder_file:
            job_queue_label_encoder: LabelEncoder = pickle.load(label_encoder_file)
            
        return job_queue_label_encoder

    @staticmethod
    def load_keras_model(file_path: str) -> tf.keras.models.Sequential:
        """
        Load a Keras Sequential model from a H5 file.

        Args:
            file_path (str): The path to the H5 file containing the Keras model.

        Returns:
            tf.keras.models.Sequential: The loaded Keras Sequential model.
        """
        job_queue_model: tf.keras.models.Sequential = keras.models.load_model(file_path)
        
        return job_queue_model
