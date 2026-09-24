from typing import Literal

from hermes._rust.er.methods.exact import exact

METHODS = [
    exact
]

def resolve(given: str, candidate: str, methods: Literal[METHODS], threshold: float|None = None):
    scores = []
        
    if len(methods) == 0:
        for method in METHODS:
            score = method(given, candidate)
            scores.append(score)
    else:
        for method in methods:
            score = method(given, candidate)
            scores.append(score)
    rep = {
        'scores': scores,
        'mean' : mean(scores)
    } 
    if threshold is not None:
        rep['above_threshold'] = [score for score in scores if score <= threshold]
    
    return rep