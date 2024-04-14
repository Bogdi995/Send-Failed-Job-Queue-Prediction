import re
import os
import spacy
import spellchecker
from typing import Callable
from nltk.corpus import stopwords
from spellchecker import SpellChecker


class TextPreprocessing:
    
    @staticmethod
    def lower_text(text: str) -> str:
        """
        Convert the words in the text to lowercase.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The converted text with all lowercase words.
        """
        return text.lower()

    @staticmethod
    def replace_abbreviations(text: str, contractions: dict[str, str]) -> str:
        """
        Replaces abbreviations with their long form.

        Args:
            text (str): The text to be adjusted.
            contractions (dict[str, str]): Dictionary of contractions.

        Returns:
            str: The adjusted text with expanded abbreviations.
        """
        text = text.split()
        new_text: list[str] = []
        for word in text:
            if word in contractions:
                new_text.append(contractions[word])
            else:
                new_text.append(word)
        text = " ".join(new_text)
        
        return text

    @staticmethod
    def remove_unimportant_data(text: str) -> str:
        """
        Formats words and removes links and unwanted characters such as quotes, periods, etc.

        Args:
            text (str): The text to be adjusted.

        Returns:
            str: The adjusted text with removed unimportant data.
        """
        new_text: str = re.sub(r"https?:\/\/.*[\r\n]*", "", text, flags=re.MULTILINE)
        new_text = re.sub(r"\<a href", " ", new_text)
        new_text = re.sub(r"&amp;", "", new_text) 
        new_text = re.sub(r"[_'\-;%()|+&=*%.,!?:#$@\[\]/]", " ", new_text)
        new_text = re.sub(r"<br />", " ", new_text)
        new_text = re.sub(r"\"", " ", new_text)
        
        return new_text

    @staticmethod
    def remove_stopwords(text: str) -> str:
        """
        Removes unnecessary words from the text.

        Args:
            text (str): The text to be adjusted.

        Returns:
            str: The adjusted text with stopwords removed.
        """
        new_text: str = text.split()
        stops: set = set(stopwords.words("german"))
        new_text = [w for w in new_text if not w in stops]
        new_text = " ".join(new_text)
        
        return new_text

    @staticmethod
    def correct_spelling(text: str, file_path: str) -> str:
        """
        Corrects spelling mistakes in the given text.

        Args:
            text (str): The text to be adjusted.
            file_path (str): The path of the text file to read the custom spelling from.

        Returns:
            str: The adjusted text with spelling mistakes corrected.
        """ 
        spell: spellchecker = SpellChecker(language="de")
        spell.word_frequency.load_text_file(file_path)
        corrected_text: list[str] = []
        words: list[str] = text.split()
        
        for word in words:
            corrected_word: str = spell.correction(word)
            corrected_text.append(word if word in spell else corrected_word if isinstance(corrected_word, str) else word)

        text = " ".join(corrected_text)
        
        return text

    @staticmethod
    def lemmatize_text(text: str, spacy_trained_pipeline: str) -> str:
        """
        Lemmatizes the words from the given text.

        Args:
            text (str): The text to be lemmatized.
            spacy_trained_pipeline: (str): The trained pipeline from spacy that will be used.

        Returns:
            str: The lemmatized text.
        """
        nlp: spacy.Language = spacy.load(spacy_trained_pipeline)
        doc: spacy.tokens.Doc = nlp(text)
        
        lemmas: list[str] = [token.lemma_ for token in doc]
        lemmatized_text: str = " ".join(lemmas)
        
        return lemmatized_text

    @staticmethod
    def clean_text(text: str, contractions: dict[str, str], spelling_file_path: str, spacy_trained_pipeline: str) -> list[str]:
        """
        Cleans the text by removing unwanted characters, stopwords, and lemmatizing the text.

        Args:
            text (str): The text to be cleaned.
            contractions (dict[str, str]): Dictionary of contractions.
            file_path (str): The path of the text file to read the custom spelling from.
            spacy_trained_pipeline: (str): The trained pipeline from spacy that will be used.

        Returns:
            list[str]: The cleaned text as a list of strings.
        """
        text = TextPreprocessing.lower_text(text)
        text = TextPreprocessing.remove_unimportant_data(text)
        text = TextPreprocessing.replace_abbreviations(text, contractions)
        text = TextPreprocessing.remove_stopwords(text)
        text = TextPreprocessing.correct_spelling(text, spelling_file_path)
        text = TextPreprocessing.lemmatize_text(text, spacy_trained_pipeline)
        
        return text

    @staticmethod
    def preprocess_utterance(user_utterance: str, 
                             preprocessing_functions: dict[str, Callable[[str], str]], 
                             contractions: dict[str, str],
                             config: dict[str, any]
    ) -> str:
        """
        Preprocesses the user utterance using the provided preprocessing functions.

        Args:
            user_utterance (str): The utterance to be preprocessed.
            preprocessing_functions (dict[str, Callable[[str], str]]): Dictionary of preprocessing functions.
            contractions (dict[str, str]): Dictionary of contractions.
            config (dict[str, any]): The configuration file.

        Returns:
            str: The preprocessed user utterance.
        """
        processed_utterance: str = user_utterance
        parent_script_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        for function_name, function in preprocessing_functions.items():
            switch = {
                "lowercase": lambda: function(processed_utterance),
                "remove_unimportant": lambda: function(processed_utterance),
                "replace_abbreviations": lambda: function(processed_utterance, contractions),
                "remove_stopwords": lambda: function(processed_utterance),
                "correct_spelling": lambda: function(processed_utterance, os.path.join(parent_script_dir, config['paths']['spelling'])),
                "lemmatize": lambda: function(processed_utterance, config['spacy']['trained_pipeline']),
            }
        
            processed_utterance = switch.get(function_name, lambda: processed_utterance)()

        return processed_utterance