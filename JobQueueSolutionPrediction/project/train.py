import os
import sys
import spacy
import warnings
import numpy as np 
import tensorflow as tf
from collections import Counter
from typing import Union, Callable
from keras.models import Sequential
warnings.filterwarnings("ignore")

sys.path.append('src')

from src.data_saving import DataSaving
from src.data_loading import DataLoading
from src.data_processing import DataProcessing
from src.data_augmentation import DataAugmentation
from src.model_training import ModelTraining
from src.text_preprocessing import TextPreprocessing
from src.named_entity_recognition import NamedEntityRecognition


def load_configuration(script_dir: str) -> dict[str, any]:
    """
    Load configuration from the config.json file.

    Args:
        script_dir: str: The script directory path.

    Returns:
        dict[str, any]: Configuration dictionary.
    """
    config_path: str = os.path.join(script_dir, 'config.json')

    return DataLoading.load_config(config_path)

def load_intents(config: dict[str, any], script_dir: str) -> dict[str, list[str]]:
    """
    Load the intents from the path specified in the configuration.

    Args:
        config (dict[str, any]): Configuration dictionary.
        script_dir: str: The script directory path.

    Returns:
        dict[str, list[str]]: Intents dictionary.
    """
    intents_path: str = os.path.join(script_dir, config['paths']['intents'])

    return DataLoading.load_intents(intents_path)

def process_training_data(intents: dict[str, list[str]],
                          config: dict[str, any],
                          script_dir: str
) -> tuple[list[str], list[str], list[str]]:
    """
    Process training data, augment it, and prepare related data structures.

    Args:
        intents (dict[str, list[str]]): Intents dictionary.
        config (dict[str, any]): Configuration dictionary.
        script_dir: str: The script directory path.

    Returns:
        tuple[list[str], list[str], list[str]]: Tuple containing augmented training utterances, augmented training labels and labels.
    """
    training_utterances: list[str] = DataProcessing.get_training_utterances(intents)
    training_labels: list[str] = DataProcessing.get_training_labels(intents)
    labels: list[str] = DataProcessing.get_labels(intents)

    data_augmentation = DataAugmentation()

    stopwords_path: str = os.path.join(script_dir, config['paths']['stopwords'])
    aug_stopwords: list[str] = DataLoading.load_stopwords(stopwords_path)

    aug_training_utterances, aug_training_labels = data_augmentation.get_augmented_utterances_labels(
        training_utterances, training_labels, Counter(training_labels), aug_stopwords, config['data_augmentation']['utterances_length']
    )

    aug_training_utterances: list[str] = [x.replace("=", " ").replace("'", " ") for x in aug_training_utterances]

    return aug_training_utterances, aug_training_labels, labels

def load_entities_and_train_ner(aug_training_utterances: list[str],
                                config: dict[str, any],
                                script_dir: str
) -> NamedEntityRecognition:
    """
    Load entities, train NER, and extract/replaces entities in the training utterances.

    Args:
        aug_training_utterances (list[str]): Augmented training utterances.
        config (dict[str, any]): Configuration dictionary.
        script_dir: str: The script directory path.

    Returns:
        NamedEntityRecognition: The trained NLP object.
    """
    entities_path: str = os.path.join(script_dir, config['paths']['entities'])
    training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]] = NamedEntityRecognition.get_training_data(aug_training_utterances, entities_path, config['spacy']['trained_pipeline'])
    trained_nlp: spacy.Language = NamedEntityRecognition.train_ner(training_data, config['ner']['iterations'])[0]
    aug_training_utterances: list[str] = NamedEntityRecognition.replace_entities(aug_training_utterances, trained_nlp)
    
    return aug_training_utterances, trained_nlp

def preprocess_training_utterances(aug_training_utterances: list[str], config: dict[str, any], script_dir: str) -> list[str]:
    """
    Preprocess training utterances using various text preprocessing techniques.

    Args:
        aug_training_utterances (list[str]): Augmented training utterances.
        config (dict[str, any]): Configuration dictionary.
        script_dir: str: The script directory path.

    Returns:
        list[str]: List of preprocessed training utterances.
    """
    spelling_path: str = os.path.join(script_dir, config['paths']['spelling'])
    contractions_path: str = os.path.join(script_dir, config['paths']['contractions'])
    contractions: dict[str, str] = DataLoading.load_contractions(contractions_path)

    preprocessed_training_utterances: list[str] = []
    for i, utterance in enumerate(aug_training_utterances):
        preprocessed_utterance: str = TextPreprocessing.clean_text(utterance, contractions, spelling_path, config['spacy']['trained_pipeline'])
        preprocessed_training_utterances.append(preprocessed_utterance)

        if (i + 1) % 10 == 0 or (i + 1) == len(aug_training_utterances):
            print(f'Processed {i + 1} utterances.')
    
    return preprocessed_training_utterances

def load_and_process_vocabulary_model_training(config: dict[str, any]) -> ModelTraining:
    """
    Load vocabulary, model configurations, and initialize ModelTraining object.

    Args:
        config (dict[str, any]): Configuration dictionary.

    Returns:
        ModelTraining: Initialized ModelTraining object.
    """
    vocabulary: dict[str, int] = config.get("vocabulary", {})
    model: dict[str, Union[int, str, float]] = config.get("model", {})
    training: dict[str, int] = config.get("training", {})
    
    return ModelTraining(vocabulary, model, training)

def train_model(model_training: ModelTraining, 
                preprocessed_training_utterances: list[str], 
                aug_training_labels: list[str], 
                labels:list[str]
) -> Sequential:
    """
    Train the model.

    Args:
        model_training (ModelTraining): Initialized ModelTraining object.
        preprocessed_training_utterances (list[str]): List of preprocessed training utterances.
        aug_training_labels (list[str]): List of augmented training labels.
        labels (list[str]): The list of labels.
        
    Returns:
        Sequential: The trained Keras model.
    """
    tf.random.set_seed(42)

    training_labels_encoded: np.ndarray = model_training.get_training_labels_encoded(aug_training_labels)
    vectorized_preprocessed_training_utterances: str = model_training.get_vectorized_preprocessed_training_utterances(preprocessed_training_utterances)

    num_labels = len(labels)
    model = model_training.get_model(num_labels)
    history = model.fit(vectorized_preprocessed_training_utterances,
                        tf.convert_to_tensor(training_labels_encoded), epochs=model_training.training['epochs'])

    return model

def save_objects(model_training: ModelTraining, 
                 trained_nlp: NamedEntityRecognition,
                 model: Sequential,
                 config: dict[str, any], 
                 script_dir: str) -> None:
    """
    Save the trained NLP, Keras model, vectorizer, label encoder, and preprocessing functions.

    Args:
        model_training (ModelTraining): Initialized ModelTraining object.
        trained_nlp (NamedEntityRecognition): The trained NER model. 
        model (Sequential): The trained Keras model
        config (dict[str, any]): Configuration dictionary.
        script_dir: str: The script directory path.

    Returns:
        None
    """
    preprocessing_functions: dict[str, Callable[[str], str]] = {
        "lowercase": TextPreprocessing.lower_text,
        "remove_unimportant": TextPreprocessing.remove_unimportant_data,
        "replace_abbreviations": TextPreprocessing.replace_abbreviations,
        "remove_stopwords": TextPreprocessing.remove_stopwords,
        "correct_spelling": TextPreprocessing.correct_spelling,
        "lemmatize": TextPreprocessing.lemmatize_text
    }
    
    nlp_path: str = os.path.join(script_dir, config['paths']['nlp'])
    model_path: str = os.path.join(script_dir, config['paths']['model'])
    vectorizer_path: str = os.path.join(script_dir, config['paths']['vectorizer'])
    label_encoder_path: str = os.path.join(script_dir, config['paths']['label_encoder'])
    preprocessing_functions_path: str = os.path.join(script_dir, config['paths']['preprocessing_functions'])

    DataSaving.save_trained_nlp(trained_nlp, nlp_path)
    DataSaving.save_keras_model(model, model_path)
    DataSaving.save_vectorizer(model_training.vectorize_layer, vectorizer_path)
    DataSaving.save_label_encoder(model_training.label_encoder, label_encoder_path)
    DataSaving.save_preprocessing_functions(preprocessing_functions, preprocessing_functions_path)

def train():
    """
    Main function to train the prediction model.

    Args:
        None

    Returns:
        None
    """
    script_dir: str = os.path.dirname(os.path.realpath(__file__))
    config: dict[str, any] = load_configuration(script_dir)
    intents: dict[str, list[str]] = load_intents(config, script_dir)

    aug_training_utterances, aug_training_labels, labels = process_training_data(intents, config, script_dir)
    aug_training_utterances, trained_nlp = load_entities_and_train_ner(aug_training_utterances, config, script_dir)
    preprocessed_training_utterances: list[str] = preprocess_training_utterances(aug_training_utterances, config, script_dir)
    model_training: ModelTraining = load_and_process_vocabulary_model_training(config)
    model: Sequential = train_model(model_training, preprocessed_training_utterances, aug_training_labels, labels)

    save_objects(model_training, trained_nlp, model, config, script_dir)

if __name__ == "__main__":
    train()