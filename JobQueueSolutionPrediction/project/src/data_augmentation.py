import math
import nlpaug.augmenter.word as naw
from collections import Counter


class DataAugmentation:

    def __init__(self):
        self.aug_bert_insert = naw.ContextualWordEmbsAug(
            model_path="distilbert-base-german-cased",
            model_type="bert",
            action="insert",
            top_k=10
        )

        self.aug_bert_substitute = naw.ContextualWordEmbsAug(
            model_path="distilbert-base-german-cased",
            model_type="bert",
            action="substitute",
            top_k=10
        )

    def get_augmented_utterances_labels(
        self,
        training_utterances: list[str], 
        training_labels: list[str], 
        label_counts: Counter, 
        aug_stopwords: list[str], 
        no_utterances: int
    ) -> tuple[list[str], list[str]]:
        """
        Creates augmented utterances for each label so that each label will have exaclty n utterances.

        Args:
            training_utterances (list[str]): The list of utterances.
            training_labels (list[str]): The list of labels.
            label_counts (Counter): Keeps track of the frequency of all labels in the dataset.
            aug_stopwords (list[str]): A list of words that will not be replaced the augmented sentences.
            no_utterances (int): The number of utterances that should exist per label.

        Returns:
            tuple[list[str], list[str]]: A tuple with the augmented utterances and labels.
        """ 
        aug_training_utterances: list[str] = []
        aug_training_labels: list[str] = []
        
        for idx, (label, count) in enumerate(label_counts.items(), 1):
            utterances: list[str] = self.get_utterances(label, training_labels, training_utterances)
            aug_training_utterances.extend(utterances)
            
            if (no_utterances > count):
                no_utterances_to_be_augmented: int = no_utterances - count
                augmented_utterances: list[str] = self.get_augmented_utterances(utterances[0], aug_stopwords, no_utterances_to_be_augmented)
                augmented_labels: list[str] = [label] * no_utterances
                aug_training_utterances.extend(augmented_utterances)    
            else:
                augmented_labels: list[str] = [label] * count

            aug_training_labels.extend(augmented_labels)

            if idx % 10 == 0 or idx == len(label_counts):
                print(f"Processed {idx} labels.")
            
        return aug_training_utterances, aug_training_labels

    @staticmethod
    def get_utterances(target_label: str, training_labels: list[str], training_utterances: list[str]) -> list[str]:
        """
        Finds the utterances for a given label.

        Args:
            target_label (str): The label for which the utterance is searched.
            training_labels (list[str]): The list of labels.
            training_utterances (list[str]): The list of utterances.

        Returns:
            list[str]: A list with the utterances for the given label.
        """
        utterances: list[str] = []
        
        for i, label in enumerate(training_labels):
            if label == target_label:
                utterances.append(training_utterances[i])

        return utterances

    def get_augmented_utterances(self, utterance: str, aug_stopwords: list[str], no_utterances: int) -> list[str]:
        """
        Creates n augmented utterances for the given utterance.

        Args:
            utterance (str): The utterance that will be augmented.
            aug_stopwords (list[str]): A list of words that will not be replaced in the augmented sentences.
            no_utterances (int): The number of utterances that will be created.

        Returns:
            list[str]: The new augmented utterances.
        """
        aug_utterances_inserted: list[str] = []
        aug_utterances_substitued: list[str] = []
        
        aug_utterances_inserted = self.aug_bert_insert.augment(utterance, n=math.ceil(no_utterances/2))
        if (no_utterances > 1):
            aug_utterances_substitued = self.aug_bert_substitute.augment(utterance, n=math.floor(no_utterances/2))
            
        aug_combined: list[str] = aug_utterances_inserted + aug_utterances_substitued
        augmented_utterances: list[str] = self.replace_aug_stopwords(aug_combined, self.get_aug_stopwords(utterance, aug_stopwords))

        return augmented_utterances

    @staticmethod
    def replace_aug_stopwords(aug_utterances: list[str], aug_stopwords: list[str]) -> list[str]:
        """
        Replaces [UNK] with the stopwords from the given list in each sentence of the `aug_utterances`.

        Args:
            aug_utterances (list[str]): A list of augmented utterances.
            aug_stopwords (list[str]): A list of stopwords to replace [UNK] in the augmented utterances.

        Returns:
            list[str]: A new list of utterances with [UNK] replaced by the corresponding stopwords.
        """
        new_aug_utterances: list[str] = []
        
        for utterance in aug_utterances:
            for word in aug_stopwords:
                utterance = utterance.replace("[UNK]", word, 1)
            new_aug_utterances.append(utterance)
        
        return new_aug_utterances

    @staticmethod
    def get_aug_stopwords(utterance: str, aug_stopwords: list[str]) -> list[str]:
        """
        Finds stopwords from the given list in the `utterance`.

        Args:
            utterance (str): The input utterance to search for stopwords.
            aug_stopwords (list[str]): A list of stopwords to search for in the `utterance`.

        Returns:
            list[str]: A list of strings containing the stopwords found in the `utterance`.
        """
        found_stopwords: list[str] = []
        
        for word in aug_stopwords:
            if word in utterance:
                found_stopwords.append(word)
        
        return found_stopwords