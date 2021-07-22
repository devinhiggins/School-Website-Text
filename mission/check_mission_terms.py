import re
import spacy
from spacy.matcher import PhraseMatcher

from mission.deny_vip_list import mission_terms


def check_mission_terms(text_list, miss_terms=mission_terms):
    """
    Using phrases & keywords from various qualitative researches
    on the mission statements and spaCy's phraseMatcher, we
    efficiently match large terminology lists

    Args:
        text_list (list): List of positively predicted texts from One-Class SVM

        miss_terms (list, default=mission_terms): List of phrases and keywords

    Returns:
        dict{text, number of matches}: Sorted dict in descending order based on number of matches
    """
    print('Checking for the mission terms start', flush=True)
    text_point_dic = {}

    nlp = spacy.load("en_core_web_lg")  # load spaCy's English model
    # PhraseMatcher accepts match patterns in the form of Doc objects
    matcher = PhraseMatcher(nlp.vocab)
    # run nlp.make_doc to speed things up
    patterns = [nlp.make_doc(term.lower()) for term in miss_terms]
    matcher.add("MissionTermList", patterns)

    for text in text_list:  # check for irrelevant texts & duplicates
        if re.match("^[0-9 ]+$", text):
            continue
        if text in text_point_dic:
            continue

        # find matching patterns and record number of matches in dict
        doc = nlp(text.lower())
        matches = matcher(doc)
        text_point_dic[text] = len(matches)

    # sort the dict in descending order (highest match to appear first) and return
    return {k: v for k, v in sorted(text_point_dic.items(), key=lambda item: item[1], reverse=True)}