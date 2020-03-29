"""
Find optimum sequence of actions with beam search over random trials.

Author: Nikolay Lysenko
"""


from random import choice
from typing import Any, Dict, List, Optional, Tuple

from rlmusician.environment import CounterpointEnv
from rlmusician.utils import map_in_parallel


def continue_stub(
        env: CounterpointEnv,
        stub: List[int]
) -> Tuple[List[int], float]:
    """
    Continue stub with random actions until episode is finished.

    :param env:
        environment
    :param stub:
        sequence of actions
    :return:
        finalized sequence of actions and reward for the episode
    """
    env.reset()
    done = False
    past_actions = []
    valid_actions = env.valid_actions
    for action in stub:
        observation, reward, done, info = env.step(action)
        past_actions.append(action)
        valid_actions = info['next_actions']
    while not done:
        action = choice(valid_actions)
        observation, reward, done, info = env.step(action)
        past_actions.append(action)
        valid_actions = info['next_actions']
    record = (past_actions, reward)
    return record


def update_stubs(
        records: List[Tuple[List[int], float]],
        n_stubs: int,
        stub_length: int
) -> List[List[int]]:
    """
    Create new stubs based on collected statistics.

    :param records:
        sorted statistics of played episodes as sequences of actions
        and corresponding to them rewards; elements must be sorted by reward
        in descending order
    :param n_stubs:
        number of stubs to be created
    :param stub_length:
        number of actions in each stub
    :return:
        new stubs
    """
    stubs = []
    for record in records:  # pragma: no branch
        key = record[0][:stub_length]
        if key not in stubs:
            stubs.append(key)
        if len(stubs) == n_stubs:
            break
    return stubs


def optimize_with_bsmc(
        env: CounterpointEnv,
        beam_width: int,
        n_records_to_keep: int,
        n_trials_schedule: List[int],
        paralleling_params: Optional[Dict[str, Any]] = None
) -> List[List[int]]:
    """
    Find optimum sequences of actions with Beam Search Monte Carlo method.

    :param env:
        environment
    :param beam_width:
        number of best subsequences to be kept after each iteration
    :param n_records_to_keep:
        number of best played episodes to be kept after each iteration
    :param n_trials_schedule:
        numbers of random continuations of each stub at
        corresponding iteration; the last element is used for all further
        iterations if there are any
    :param paralleling_params:
        settings of parallel playing of episodes;
        by default, number of processes is set to number of cores
        and each worker is not replaced with a newer one after some number of
        tasks are finished
    :return:
        best final sequences of actions
    """
    stubs = [[]]
    records = []
    paralleling_params = paralleling_params or {}
    n_measures_to_fill = env.piece.n_measures - 2
    for i in range(n_measures_to_fill):
        n_trials = n_trials_schedule[min(i, len(n_trials_schedule) - 1)]
        for stub in stubs:
            records_for_stub = map_in_parallel(
                continue_stub,
                [(env, stub) for _ in range(n_trials)],
                paralleling_params
            )
            records.extend(records_for_stub)
        records = sorted(records, key=lambda x: x[1], reverse=True)
        print(
            f"Current best reward: {records[0][1]:.5f}, "
            f"achieved with: {records[0][0]}."
        )
        stubs = update_stubs(records, beam_width, i + 1)
        records = records[:n_records_to_keep]
    return stubs
