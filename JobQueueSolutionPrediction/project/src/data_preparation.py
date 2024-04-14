import json


def load_data(path: str) -> dict[str, list[str]]:
    """
    Loads data from a JSON file and returns it as a dictionary.

    Args:
        path (str): The path to the JSON file.

    Returns:
        dict[str, list[str]]: A dictionary containing lists of training utterances, labels, responses, and unique labels.
    """
    with open(path, encoding ="utf-8") as file:
        data: dict[str, list[str]] = json.load(file)
    
    return data


def get_training_utterances(data: dict[str, list[str]]) -> list[str]:
    """
    Extracts training utterances from the loaded data.

    Args:
        data (dict[str, list[str]]): The loaded data.

    Returns:
        list[str]: A list of training utterances.
    """
    training_utterances: list[str] = []

    for intent in data["intents"]:
        for utterance in intent["utterances"]:
            training_utterances.append(utterance)
    
    return training_utterances


def get_training_labels(data: dict[str, list[str]]) -> list[str]:
    """
    Extracts training labels from the loaded data.

    Args:
        data (dict[str, list[str]]): The loaded data.

    Returns:
        list[str]: A list of training labels.
    """
    training_labels: list[str] = []

    for intent in data["intents"]:
        for utterance in intent["utterances"]:
            training_labels.append(intent["tag"])
    
    return training_labels


def get_labels(data: dict[str, list[str]]) -> list[str]:
    """
    Extracts unique labels from the loaded data.

    Args:
        data (dict[str, list[str]]): The loaded data.

    Returns:
        list[str]: A list of unique labels.
    """
    labels: list[str] = []

    for intent in data["intents"]:
        if intent["tag"] not in labels:
            labels.append(intent["tag"])
    
    return labels

