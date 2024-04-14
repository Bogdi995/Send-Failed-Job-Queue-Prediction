import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter


class DataVisualization:

    @staticmethod
    def plot_counter(training_labels: list[str], color="maroon") -> None:
        """
        Plot the number of labels as a horizontal bar chart.

        Args:
            training_labels (list[str]): The list of labels.
            color (str, optional): The color of the bars. Defaults to 'maroon'.

        Returns:
            None
        """
        label_counts: Counter = Counter(training_labels)
        intent: list[str] = list(label_counts.keys())
        no_utterances: list[int] = list(label_counts.values())
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        ax.barh(intent, no_utterances, color=color)
        
        ax.set_xlabel("No of utterances")
        ax.set_ylabel("Intent")
        ax.set_title("No of utterances for each intent")
        ax.tick_params(axis="y", pad=8)
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", linewidth=0.5)
        
        for i, value in enumerate(no_utterances):
            ax.text(value + 0.2, i, str(value), va="center")
        
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_utterances_length(utterances: list[str], color="maroon") -> None:
        """
        Plot the distribution of utterance lengths as a bar chart.

        Args:
            utterances (list[str]): The utterances that will be plottted.
            color (str, optional): The color of the bars. Defaults to 'maroon'.

        Returns:
            None
        """
        utterance_lengths: list[int] = [len(utterance) for utterance in utterances]
        
        plt.figure(figsize=(10, 6))
        plt.hist(utterance_lengths, bins=30, edgecolor="black", alpha=0.7, color=color)
        
        plt.xlabel("Utterance Length")
        plt.ylabel("Frequency")
        plt.title("Distribution of Utterance Lengths")
        
        plt.grid(axis="y", linestyle="--", linewidth=0.5)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def visualize_loss(training_loss: list[float], color: str="maroon") -> None:
        """
        Visualize the training loss at each iteration.

        Args:
            training_loss (list[float]): The list of training losses.
            color (str, optional): Color for the visualization. Defaults to "maroon".

        Returns:
            None
        """
        plt.figure(figsize=(10, 6))
        plt.plot([*range(len(training_loss))], training_loss, color=color)

        plt.xlabel("Iteration Number")
        plt.ylabel("Loss")
        plt.title("Loss at every iteration")
        
        plt.tick_params(axis="y", pad=8)
        plt.grid(axis="x", linestyle="--", linewidth=0.5)
        plt.tight_layout()
        
        plt.show()

    @staticmethod
    def plot_wordcloud(utterances: str) -> None:
        """
        Generates and displays a word cloud visualization of the most frequent words in the utterances.

        Args:
            utterances (str): The preprocessed utterances concatenated into a single string.

        Returns:
            None
        """
        wordcloud = WordCloud(width=1000, height=600, background_color="white").generate(utterances)

        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Most Frequent Words in Utterances")
        plt.show()

    @staticmethod
    def plot_confusion_matrix(cm: np.ndarray) -> None:
        """
        Plots a confusion matrix using a heatmap.
        
        Args:
            cm (np.ndarray): The confusion matrix to plot.

        Returns:
            None
        """
        plt.figure(figsize=(14, 14))
        sns.heatmap(cm, annot=True, cmap="Blues")

        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title("Confusion Matrix")

        plt.show()
