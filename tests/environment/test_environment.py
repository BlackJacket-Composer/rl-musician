"""
Test `rlmusician.environment.environment` module.

Author: Nikolay Lysenko
"""


from typing import List

import numpy as np
import pytest

from rlmusician.environment import PianoRollEnv


class TestPianoRollEnv:
    """Tests for `PianoRollEnv` class."""

    @pytest.mark.parametrize(
        "env, actions, expected",
        [
            (
                # `env`
                PianoRollEnv(
                    n_semitones=5,
                    n_roll_steps=5,
                    n_observed_roll_steps=3,
                    max_n_stalled_episode_steps=2,
                    scoring_coefs={'absence_of_outer_notes': 1},
                    scoring_fn_params={},
                    padding_mean=0.1,
                    rendering_params={}
                ),
                # `actions`
                [2] + [0 for _ in range(7)],
                # `expected`
                -1
            )
        ]
    )
    def test_step(
            self, env: PianoRollEnv, actions: List[int], expected: float
    ) -> None:
        """Test `step` method."""
        env.reset()
        for action in actions:
            observation, reward, done, info = env.step(action)
        assert done
        assert reward == expected

    @pytest.mark.parametrize(
        "env, expected",
        [
            (
                # `env`
                PianoRollEnv(
                    n_semitones=5,
                    n_roll_steps=5,
                    n_observed_roll_steps=3,
                    max_n_stalled_episode_steps=2,
                    scoring_coefs={'absence_of_outer_notes': 1},
                    scoring_fn_params={},
                    padding_mean=0,
                    rendering_params={}
                ),
                # `expected`
                np.zeros((5, 3))
            )
        ]
    )
    def test_reset(self, env: PianoRollEnv, expected: np.ndarray) -> None:
        """Test `reset` method."""
        observation = env.reset()
        np.testing.assert_equal(observation, expected)
        assert env.n_episode_steps_passed == 0
        assert env.n_piano_roll_steps_passed == 0
        assert env.n_stalled_episode_steps == 0
