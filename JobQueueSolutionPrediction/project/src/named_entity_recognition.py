import sys
import spacy
from typing import Union
from spacy import displacy
from spacy.matcher import Matcher, PhraseMatcher

sys.path.append('src')

from src.data_loading import DataLoading


class NamedEntityRecognition:
    
    @staticmethod
    def create_matcher(nlp: spacy.Language) -> Matcher:
        """
        Create a Matcher object for pattern matching.

        Args:
            nlp (spacy.Language): The Spacy language model.

        Returns:
            Matcher: The created Matcher object.
        """
        matcher: Matcher = Matcher(nlp.vocab)

        pattern_numbers: list[dict[str, dict[str, str]]] = [{"TEXT": {"REGEX": r"\d+"}}]
        pattern_users: list[dict[str, dict[str, str]]] = [{"TEXT": {"REGEX": "^FUM-GLOBAL\\\\[A-Za-z]+(?:\\.[A-Za-z]+)?$"}}]
        pattern_emails: list[dict[str, dict[str, str]]] = [{"TEXT": {"REGEX": "[a-z0-9\.\-+_]+ *@[a-z0-9\.\-+_]+"}}]

        matcher.add("Nummer", [pattern_numbers])
        matcher.add("Benutzer", [pattern_users])
        matcher.add("Email", [pattern_emails])

        return matcher

    @staticmethod
    def create_phrase_matcher(nlp: spacy.Language, entities_dict: dict[str, list[str]]) -> PhraseMatcher:
        """
        Create a PhraseMatcher object for phrase matching.

        Args:
            nlp (spacy.Language): The Spacy language model.
            entities_dict (dict[str, list[str]]): Dictionary containing entities and their values.

        Returns:
            PhraseMatcher: The created PhraseMatcher object.
        """
        phrase_matcher: PhraseMatcher = PhraseMatcher(nlp.vocab)

        for key, values in entities_dict.items():
            phrase_patterns: list[spacy.tokens.Doc] = [nlp(value) for value in values]
            phrase_matcher.add(key, phrase_patterns)

        return phrase_matcher

    @staticmethod
    def find_entities(
        nlp: spacy.Language,
        matcher: Matcher,
        phrase_matcher: PhraseMatcher,
        aug_training_utterances: list[str]
    ) -> list[tuple[str, dict[str, list[tuple[int, int, str]]]]]:
        """
        Find entities in the given training utterances using the provided matchers.

        Args:
            nlp (spacy.Language): The Spacy language model.
            matcher (Matcher): The Matcher object for pattern matching.
            phrase_matcher (PhraseMatcher): The PhraseMatcher object for phrase matching.
            aug_training_utterances (list[str]): List of training utterances.

        Returns:
            list[tuple[str, dict[str, list[tuple[int, int, str]]]]]: List of tuples containing the utterances and the detected entities.
        """
        training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]] = []

        for utterance in aug_training_utterances:
            doc: spacy.Language = nlp(utterance)
        
            matches: list[tuple[int, int, int]] = matcher(doc)
            phrase_matches: list[tuple[int, int, int]] = phrase_matcher(doc)
            
            entities: list[tuple[int, int, str]] = []
            for match_id, start, end in matches:
                entity_name: str = nlp.vocab.strings[match_id]
                entities.append((doc[start].idx, doc[end - 1].idx + len(doc[end - 1]), entity_name))
        
            for match_id, start, end in phrase_matches:
                entity_name: str = nlp.vocab.strings[match_id]
                entities.append((doc[start].idx, doc[end - 1].idx + len(doc[end - 1]), entity_name))
        
            training_data.append((utterance, {"entities": entities}))

        return training_data

    @staticmethod
    def get_training_data(aug_training_utterances: list[str], entities_path: str, spacy_trained_pipeline: str) -> list[tuple[str, dict[str, list[tuple[int, int, str]]]]]:
        """
        Process training data by loading models, entities, creating matchers, and finding entities in the utterances.

        Args:
            aug_training_utterances (list[str]): List of training utterances.
            entities_path (str): The path of the text file to read entities from.
            spacy_trained_pipeline: (str): The trained pipeline from spacy that will be used.
            
        Returns:
            list[tuple[str, dict[str, list[tuple[int, int, str]]]]]: Processed training data with found entities.
        """
        nlp: spacy.Language = spacy.load(spacy_trained_pipeline)
        
        entities_dict: dict[str, list[str]] = DataLoading.load_entities(entities_path)
        
        matcher: Matcher = NamedEntityRecognition.create_matcher(nlp)
        phrase_matcher: PhraseMatcher = NamedEntityRecognition.create_phrase_matcher(nlp, entities_dict)
        
        training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]] = NamedEntityRecognition.find_entities(
            nlp, matcher, phrase_matcher, aug_training_utterances)

        return training_data

    @staticmethod
    def create_ner_model() -> spacy.Language:
        """
        Create a blank Spacy Language model with the `ner` component.

        Args:
            None

        Returns:
            spacy.Language: The created Spacy Language model.
        """
        nlp: spacy.Language = spacy.blank("de")
        nlp.add_pipe("ner") if "ner" not in nlp.pipe_names else nlp.get_pipe("ner")
        
        return nlp

    @staticmethod
    def add_labels_to_ner_model(nlp: spacy.Language, training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]]) -> None:
        """
        Add entity labels from the training data to the NER model.

        Args:
            nlp (spacy.Language): The Spacy Language model.
            training_data (list[tuple[str, dict[str, list[tuple[int, int, str]]]]]): The training data.

        Returns:
            None
        """
        ner: spacy.pipeline.ner.EntityRecognizer = nlp.get_pipe("ner")
        
        for _, annotations in training_data:
            for entity in annotations.get("entities"):
                ner.add_label(entity[2])

    @staticmethod
    def train_ner_model(
        nlp: spacy.Language, 
        training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]], 
        iterations: int
    ) -> tuple[spacy.Language, list[float]]:
        """
        Train the NER model using the provided training data.

        Args:
            nlp (spacy.Language): The Spacy Language model.
            training_data (list[tuple[str, dict[str, list[tuple[int, int, str]]]]]): The training data.
            iterations (int): The number of training iterations.

        Returns:
            tuple[spacy.Language, list[float]]: The trained Spacy Language model and the list of training losses.
        """
        # Disable all pipes other than 'ner' during training
        other_pipes: list[str] = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        
        with nlp.disable_pipes(*other_pipes):  # only train NER
            nlp.begin_training()
            training_loss: list[float] = []
            
            for iteration in range(iterations):
                print("Starting iteration " + str(iteration))
                losses: dict[str, float] = {}
                
                for batch in spacy.util.minibatch(training_data, size=2):
                    for text, annotations in batch:
                        doc: spacy.tokens.Doc = nlp.make_doc(text)
                        example: spacy.training.example.Example = spacy.training.example.Example.from_dict(doc, annotations)
                        nlp.update([example], losses=losses, drop=0.3)
                    
                training_loss.append(losses.get("ner"))
                print(f'losses (iteration {iteration}): {losses}')
            
            return nlp, training_loss

    @staticmethod
    def train_ner(training_data: list[tuple[str, dict[str, list[tuple[int, int, str]]]]], 
                  iterations: int
    ) -> tuple[spacy.Language, list[float]]:
        """
        Train the NER model using the provided training data and iterations.

        Args:
            training_data (list[tuple[str, dict[str, list[tuple[int, int, str]]]]]): The training data.
            iterations (int): The number of training iterations.

        Returns:
            tuple[spacy.Language, list[float]]: A tuple containing the trained Spacy Language model and a list of training losses.
        """
        nlp: spacy.Language = NamedEntityRecognition.create_ner_model()
        NamedEntityRecognition.add_labels_to_ner_model(nlp, training_data)
        trained_nlp, train_loss = NamedEntityRecognition.train_ner_model(nlp, training_data, iterations)

        return trained_nlp, train_loss

    @staticmethod
    def extract_entities(utterances: list[str], trained_nlp: spacy.Language, visualize: bool=False) -> list[str]:
        """
        Extracts entities from a list of utterances using a trained NER model.

        Args:
            utterances (list[str]): List of utterances to extract entities from.
            trained_nlp (spacy.Language): Trained NER model.
            visualize (bool, optional): Flag to control entity visualization. Defaults to False.

        Returns:
            list[str]: List of extracted entities for each utterance.
        """
        colors: dict[str, str] = {"Tabelle": "linear-gradient(90deg, #aa9cfc, #fc9ce7)",
                                "Feld": "linear-gradient(90deg, #abcdef, #fedcba)",
                                "Nummer": "linear-gradient(90deg, #aabbcc, #ccbbaa)",
                                "Benutzer": "linear-gradient(90deg, #aaffaa, #ffaaff)",
                                "Email": "linear-gradient(90deg, #ffff00, #00ffff)"}
        
        extracted_entities: list[str] = []
        for utterance in utterances:
            doc: spacy.Language = trained_nlp(utterance)
            ents: list[tuple[str, int, int, str]] = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
            options: dict[str, Union[list[str], dict[str, str]]] = {
                "ents": [label for _, _, _, label in ents],
                "colors": {label: colors.get(label) or "linear-gradient(90deg, #ffffff, #ffffff)" for _, _, _, label in ents}
            }
            
            if visualize:
                displacy.render(doc, style='ent', jupyter=True, options=options)
            extracted_entities.append(ents)

        return extracted_entities

    @staticmethod
    def replace_entities(aug_training_utterances: list[str], trained_nlp: spacy.Language) -> list[str]:
        """
        Replace the entities in the augmented training utterances with special tokens.

        Args:
            aug_training_utterances (list[str]): List of augmented trainging utterances.
            trained_nlp (spacy.Language): Trained NER model. 

        Returns:
            list[str]: List of the augmented training utterances with the entities replaced.
        """
        new_utterances: list[str] = []
        
        for utterance in aug_training_utterances:
            doc: spacy.Language = trained_nlp(utterance)
            ents: list[tuple[str, int, int, str]] = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]

            new_utterance: str = utterance
            for entity_text, _, _, entity_label in ents:
                placeholder = f"`ENTITÄTS{entity_label.upper()}`"
                new_utterance = new_utterance.replace(entity_text, placeholder)

            new_utterances.append(new_utterance)

        return new_utterances