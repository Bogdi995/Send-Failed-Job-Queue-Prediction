import numpy as np
import tensorflow as tf
from typing import Union
from keras.models import Sequential
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from keras.utils import pad_sequences
from keras.losses import SparseCategoricalCrossentropy
from keras.layers import TextVectorization, Dense, Embedding, MaxPooling1D, GlobalMaxPooling1D, Conv1D, Dropout


class ModelTraining:

    def __init__(self, vocabulary: dict[str, int], model: dict[str, Union[int, str, float]], training: dict[str, int]):
        self.vocabulary: dict[str, int] = vocabulary 
        self.model: dict[str, Union[int, str, float]] = model
        self.training: dict[str, int] = training
        self.label_encoder: LabelEncoder = LabelEncoder()
        self.vectorize_layer: TextVectorization = TextVectorization(max_tokens=self.vocabulary['vocab_size'], 
                                                                    output_mode="int", 
                                                                    output_sequence_length=self.vocabulary['max_sequence_length'])

    def get_training_labels_encoded(self, aug_training_labels: list[str]) -> np.ndarray:
        """
        Encode training labels using a LabelEncoder.

        Args:
            aug_training_labels (list[str]): List of training labels.

        Returns:
            np.ndarray: Encoded training labels as a NumPy array.
        """
        training_labels_encoded: np.ndarray = self.label_encoder.fit_transform(aug_training_labels)

        return training_labels_encoded

    @staticmethod
    def vectorize_text(text: list[str], vectorize_layer: TextVectorization) -> tf.Tensor:
        """
        Vectorizes the given text and returns it as a Tensor.

        Args:
            text (list[str]): The text that is going to be vectorized.
            vectorize_layer (TextVectorization): The TextVectorization layer to use for vectorization.

        Returns:
            tf.Tensor: A Tensor with the vectorized text.
        """
        new_text: tf.Tensor = tf.expand_dims(text, -1)
        
        return vectorize_layer(new_text)

    def get_vectorized_preprocessed_training_utterances(self, preprocessed_training_utterances: list[str]) -> np.ndarray:
        """
        Vectorize preprocessed training utterances using TextVectorization layer.

        Args:
            preprocessed_training_utterances (list[str]): List of preprocessed training utterances.

        Returns:
            np.ndarray: Vectorized preprocessed training utterances as a NumPy array.
        """
        self.vectorize_layer.adapt(preprocessed_training_utterances)
        vectorized_preprocessed_training_utterances = self.vectorize_text(preprocessed_training_utterances, self.vectorize_layer)

        return vectorized_preprocessed_training_utterances

    def get_model(self, num_labels: int) -> Sequential:
        """
        Creates and configures a Sequential model for text classification.
        
        Args:
            num_labels (int): The number of unique labels/classes in the classification task.
            
        Returns:
            Sequential: The configured Sequential model.
        """   
        model = Sequential()
        model.add(Embedding(self.vocabulary['vocab_size'], self.model['embedding_dim']))
        model.add(Conv1D(filters=self.model['filters'], kernel_size=self.model['kernel_size'], padding=self.model['padding'], activation=self.model['activation'], strides=self.model['strides']))
        model.add(MaxPooling1D(padding=self.model['padding'], strides=self.model['strides']))
        model.add(Conv1D(filters=self.model['filters'] * 2, kernel_size=self.model['kernel_size'], padding=self.model['padding'], activation=self.model['activation'], strides=self.model['strides']))
        model.add(MaxPooling1D(padding=self.model['padding'], strides=self.model['strides']))
        model.add(GlobalMaxPooling1D())
        model.add(Dense(units=self.model['units'] * 2, activation=self.model['activation']))
        model.add(Dropout(rate=self.model['dropout_rate']))
        model.add(Dense(units=self.model['units'], activation=self.model['activation']))
        model.add(Dropout(rate=self.model['dropout_rate']))
        model.add(Dense(num_labels, activation=self.model['final_layer_activation']))

        model.compile(
            loss=SparseCategoricalCrossentropy(from_logits=True),
            optimizer=self.model['optimizer'],
            metrics=[self.model['metric']]
        )
        
        return model

    def train_and_evaluate(
            self,
            X: np.ndarray, 
            y: np.ndarray, 
            num_folds: int, 
            labels: list[str],
            num_labels: int
    ) -> tuple[float, float, np.ndarray, str]:
        """
        Trains and evaluates a model using k-fold cross-validation.
        
        Args:
            X (np.ndarray): The input data.
            y (np.ndarray): The target labels.
            num_folds (int): The number of folds for cross-validation.
            labels: The list of the labels.
            num_labels (int): The number of unique labels/classes in the classification task.
            
        Returns:
            tuple[float, float, np.ndarray, str]: The mean loss, mean accuracy, average confusion matrix and classification report.
        """
        accuracy_scores: list[float] = []
        loss_scores: list[float] = []
        y_pred_all: list[float] = []
        y_true_all: list[float] = []
        cm: np.ndarray = np.zeros((num_labels, num_labels))

        text_vectorizer: TextVectorization = TextVectorization(max_tokens=self.vocabulary['vocab_size'], 
                                                               output_mode="int", 
                                                               output_sequence_length=self.vocabulary['max_sequence_length'])

        kf: KFold = KFold(n_splits=num_folds, shuffle=True, random_state=42)

        for train_index, val_index in kf.split(X):
            X_train: np.ndarray = X[train_index]
            X_val: np.ndarray = X[val_index]
            y_train: np.ndarray = y[train_index]
            y_val: np.ndarray = y[val_index]

            text_vectorizer.adapt(X_train)

            X_train_sequences: np.ndarray = self.vectorize_text(X_train, text_vectorizer)
            X_val_sequences: np.ndarray = self.vectorize_text(X_val, text_vectorizer)

            model: Sequential = self.get_model(num_labels)
            model.fit(X_train_sequences, y_train, epochs=self.training['epochs'], batch_size=self.training['batch_size'], verbose=0)

            X_val_sequences_padded: np.ndarray = pad_sequences(X_val_sequences, maxlen=self.vocabulary['max_sequence_length'])
            loss, accuracy = model.evaluate(X_val_sequences_padded, y_val, verbose=0)

            y_val_pred_prob: np.ndarray = model.predict(X_val_sequences_padded)
            y_val_pred: np.ndarray = np.argmax(y_val_pred_prob, axis=1)

            fold_cm: np.ndarray = confusion_matrix(y_val, y_val_pred, labels=np.arange(num_labels))
            cm += fold_cm

            loss_scores.append(loss)
            accuracy_scores.append(accuracy)
            y_pred_all.append(y_val_pred)
            y_true_all.append(y_val)

        mean_loss: float = np.mean(loss_scores)
        mean_accuracy: float = np.mean(accuracy_scores)
        cm_avg: np.ndarray = cm / num_folds

        y_pred_all = np.concatenate(y_pred_all)
        y_true_all = np.concatenate(y_true_all)

        classification_report_str: str = classification_report(y_true_all, y_pred_all, target_names=labels)

        return mean_loss, mean_accuracy, cm_avg, classification_report_str
