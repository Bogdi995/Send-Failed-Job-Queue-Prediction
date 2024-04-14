class DataProcessing:

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
