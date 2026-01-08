from rouge_metric import PyRouge
from typing import Dict, Any

def calculate_rouge(candidate_doc: str, reference_doc: str) -> Dict[str, Any]:
    """
    Calculates ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L) comparing the candidate 
    documentation against a reference.

    :param candidate_doc: Generated documentation text.
    :param reference_doc: Reference documentation text.
    :return: A dictionary containing f-measure, precision, and recall for each ROUGE metric.
    """
    rouge = PyRouge(rouge_n=(1, 2), rouge_l=True, rouge_w=False, rouge_s=False, rouge_su=False)
    
    # PyRouge expects lists of hypothesis and references
    score = rouge.evaluate([candidate_doc], [[reference_doc]])
    
    return score
