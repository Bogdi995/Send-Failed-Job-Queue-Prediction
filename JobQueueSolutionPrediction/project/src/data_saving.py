import dill
import spacy
import pickle
import tensorflow as tf
from typing import Callable
from sklearn.preprocessing import LabelEncoder


class DataSaving:

    @staticmethod
    def save_trained_nlp(trained_nlp: spacy.Language, file_path: str) -> None:
        """
        Saves the trained NLP model to a file.

        Args:
            trained_nlp (spacy.Language): The trained NLP model to be saved.
            file_path (str): The path of the file to save the trained NLP model.

        Returns:
            None
        """
        trained_nlp.to_disk(file_path)

    @staticmethod
    def save_keras_model(model: tf.keras.models.Sequential, file_path: str) -> None:
        """
        Save a Keras model to an H5 file.

        Args:
            model (tf.keras.models.Model): The Keras model to be saved.
            file_path (str): The path to save the H5 file.

        Returns:
            None
        """
        model.save(file_path)

    @staticmethod
    def save_vectorizer(vectorizer: object, file_path: str) -> None:
        """
        Save a vectorizer object using pickle.

        Args:
            vectorizer (object): The vectorizer object to be saved.
            file_path (str): The path to save the pickle file.

        Returns:
            None
        """
        with open(file_path, "wb") as vectorizer_file:
            pickle.dump({"config": vectorizer.get_config(),
                        "weights": vectorizer.get_weights()}, 
                        vectorizer_file, 
                        protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def save_label_encoder(label_encoder: LabelEncoder, file_path: str) -> None:
        """
        Save a LabelEncoder object using pickle.

        Args:
            label_encoder (LabelEncoder): The LabelEncoder object to be saved.
            file_path (str): The path to save the pickle file.

        Returns:
            None
        """
        with open(file_path, "wb") as label_encoder_file:
            pickle.dump(label_encoder, 
                        label_encoder_file, 
                        protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def save_preprocessing_functions(preprocessing_functions: dict[str, Callable[[str], str]], file_path: str) -> None:
        """
        Save a dictionary of preprocessing functions using dill and pickle.

        Args:
            preprocessing_functions (dict[str, Callable[[str], str]]): The dictionary of preprocessing functions to be saved.
            file_path (str): The path to save the pickle file.

        Returns:
            None
        """
        with open(file_path, "wb") as preprocessing_file:
            dill.dump(preprocessing_functions,
                    preprocessing_file,
                    protocol=pickle.HIGHEST_PROTOCOL)