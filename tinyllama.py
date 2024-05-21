import requests
import json
import re
from textattack.constraints import Constraint
from textattack.shared import utils

class Tinyllama(Constraint):
    def __init__(
        self,
        min_tinyllama_score=2,
        compare_against_original=True
    ):
        super().__init__(compare_against_original)
        if not isinstance(min_tinyllama_score, int):
            raise TypeError("min_tinyllama_score must be an integer")
        if min_tinyllama_score < 0:
            raise ValueError("min_tinyllama_score must be a non-negative value")

        self.min_tinyllama_score = min_tinyllama_score
        self.tinyllama_url = 'http://172.18.166.68:5011'  # Update this URL as needed

    def _mark_differences(self, text1, text2):
        words1 = text1.split()
        words2 = text2.split()

        marked_text1 = " ".join("[[{}]]".format(word) if word not in words2 else word for word in words1)
        marked_text2 = " ".join("[[{}]]".format(word) if word not in words1 else word for word in words2)

        return marked_text1, marked_text2

    def _tinyllama_sim_score(self, original_texts, adversarial_texts):
        marked_texts = [self._mark_differences(original, adversarial) for original, adversarial in zip(original_texts, adversarial_texts)]
        prompts = [
            f"Original: {marked_text[0]} \nAdversarial: {marked_text[1]}"
            for marked_text in marked_texts
        ]

        data = {'prompt': prompts}
        response = requests.post(self.tinyllama_url, json=data)

        scores = []
        res = response.json()
        for item in res['output']:
            score_part = item.split("Score:")[-1].strip()
            try:
                score = int(score_part)
            except ValueError:
                score = 1  # Default score in case of conversion failure
            scores.append(score)

        return scores

    def _check_constraint(self, transformed_text, reference_text):
        score = self._tinyllama_sim_score([reference_text.text], [transformed_text.text])[0]
        return score >= self.min_tinyllama_score

    def extra_repr_keys(self):
        return ["min_tinyllama_score"] + super().extra_repr_keys()
