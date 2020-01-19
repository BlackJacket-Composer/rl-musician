"""
Check compliance with some rules of voice leading and harmony.

Author: Nikolay Lysenko
"""


import itertools
from typing import Callable, Dict, List, Optional


def check_stability_of_rearticulated_pitch(
        line: List[Optional['LineElement']], measure: int, movement: int,
        **kwargs
) -> bool:
    """
    Check that a pitch to be rearticulated (repeated) is stable.

    :param line:
        melodic line as list of pitches
    :param measure:
        last finished measure in a line
    :param movement:
        melodic interval in scale degrees for line continuation
    :return:
        indicator whether a movement is in accordance with the rule
    """
    if movement != 0:
        return True
    return line[measure].is_from_tonic_triad


def check_that_skip_leads_to_stable_pitch(
        line: List[Optional['LineElement']],
        line_elements: List['LineElement'],
        measure: int, movement: int, **kwargs
) -> bool:
    """
    Check that a skip (leap) leads to a stable pitch.

    :param line:
        melodic line as list of pitches
    :param line_elements:
        list of pitches available for the line
    :param measure:
        last finished measure in a line
    :param movement:
        melodic interval in scale degrees for line continuation
    :return:
        indicator whether a movement is in accordance with the rule
    """
    if abs(movement) <= 1:
        return True
    next_position = line[measure].relative_position + movement
    next_element = line_elements[next_position]
    return next_element.is_from_tonic_triad


def check_that_skip_is_followed_by_opposite_step_motion(
        movement: int, previous_movements: List[int], **kwargs
) -> bool:
    """
    Check that after a large skip there is a step motion in opposite direction.

    :param movement:
        melodic interval in scale degrees for line continuation
    :param previous_movements:
        list of previous movements
    :return:
        indicator whether a movement is in accordance with the rule
    """
    if len(previous_movements) == 0:
        return True
    previous_movement = previous_movements[-1]
    if abs(previous_movement) <= 2:  # Skip of a second is not large enough.
        return True
    return movement == -previous_movement / abs(previous_movement)


def check_resolution_of_submediant_and_leading_tone(
        line: List[Optional['LineElement']], measure: int,
        movement: int, previous_movements: List[int], **kwargs
) -> bool:
    """
    Check that a sequence of submediant and leading tone properly resolves.

    If a line has submediant followed by leading tone, tonic must be used
    after leading tone, because there is strong attraction to it;
    similarly, if a line has leading tone followed by submediant,
    dominant must be used after submediant.

    :param line:
        melodic line as list of pitches
    :param measure:
        last finished measure in a line
    :param movement:
        melodic interval in scale degrees for line continuation
    :param previous_movements:
        list of previous movements
    :return:
        indicator whether a movement is in accordance with the rule
    """
    if measure < 2:
        return True
    if line[measure].is_from_tonic_triad:
        return True
    if line[measure - 1].is_from_tonic_triad:
        return True
    # If there are two unstable pitches in a row, one of them is submediant
    # and the other is leading tone.
    return movement == previous_movements[-1]


def check_step_motion_to_final_pitch(
        line: List[Optional['LineElement']],
        line_elements: List['LineElement'],
        measure: int, movement: int, **kwargs
) -> bool:
    """
    Check that there is a way to reach final pitch with step motion.

    :param line:
        melodic line as list of pitches
    :param line_elements:
        list of pitches available for the line
    :param measure:
        last finished measure in a line
    :param movement:
        melodic interval in scale degrees for line continuation
    :return:
        indicator whether a movement is in accordance with the rule
    """
    next_position = line[measure].relative_position + movement
    next_element = line_elements[next_position]
    next_degree = next_element.relative_position
    final_degree = line[-1].relative_position
    degrees_to_end_note = abs(next_degree - final_degree)
    measures_left = len(line) - measure - 2
    return degrees_to_end_note <= measures_left


def get_voice_leading_rules_registry() -> Dict[str, Callable]:
    """
    Get mapping from names to functions checking voice leading rules.

    :return:
        registry of functions checking voice leading rules
    """
    registry = {
        'rearticulation': check_stability_of_rearticulated_pitch,
        'skip_goal': check_that_skip_leads_to_stable_pitch,
        'turn_after_skip': check_that_skip_is_followed_by_opposite_step_motion,
        'two_unstable': check_resolution_of_submediant_and_leading_tone,
        'step_motion_to_end': check_step_motion_to_final_pitch
    }
    return registry


def check_consonance_of_sonority(sonority: List['LineElement']) -> bool:
    """
    Check that sonority is consonant.

    :param sonority:
        list of simultaneously sounding pitches
    :return:
        indicator whether a sonority is consonant
    """
    n_semitones_to_consonance = {
        0: True, 1: False, 2: False, 3: True, 4: True, 5: True,
        6: False, 7: True, 8: True, 9: True, 10: False, 11: False
    }
    for first, second in itertools.combinations(sonority, 2):
        interval = first.absolute_position - second.absolute_position
        interval %= len(n_semitones_to_consonance)
        if not n_semitones_to_consonance[interval]:
            return False
    return True


def check_absence_of_large_intervals(
        sonority: List['LineElement'], max_interval: int = 9
) -> bool:
    """
    Check that there are no large intervals between adjacent pitches.

    :param sonority:
        list of simultaneously sounding pitches
    :param max_interval:
        maximum allowed interval in scale degrees between two adjacent pitches
    :return:
        indicator whether a sonority has no excessive intervals
    """
    if len(sonority) == 1:
        return True
    positions = sorted(x.relative_position for x in sonority)
    adjacent_pairs = zip(positions, positions[1:])
    intervals = [y - x for x, y in adjacent_pairs]
    return max(intervals) <= max_interval


def get_harmony_rules_registry() -> Dict[str, Callable]:
    """
    Get mapping from names to functions checking harmony rules.

    :return:
        registry of functions checking harmony rules
    """
    registry = {
        'consonance': check_consonance_of_sonority,
        'absence_of_large_intervals': check_absence_of_large_intervals
    }
    return registry