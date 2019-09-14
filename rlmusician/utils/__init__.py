"""
Do auxiliary tasks.

Author: Nikolay Lysenko
"""


from .io import create_wav_from_events
from .misc import (
    apply_rolling_aggregation, shift_horizontally, shift_vertically
)


__all__ = [
    'apply_rolling_aggregation',
    'create_wav_from_events',
    'shift_horizontally',
    'shift_vertically'
]
