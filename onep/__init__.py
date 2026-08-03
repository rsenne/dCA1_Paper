"""One-photon calcium imaging analysis for the dCA1 astrocyte paper.

Importing this package re-exports the analysis API used throughout the
figure notebooks::

    import onep as op

Submodules can also be imported directly::

    from onep.cell_registration import CellReg
    from onep.trace_analysis_functions import eta_individual_cells

Data locations are not hardcoded in this package. Use :mod:`onep.paths` to
resolve the data root on the current machine; see ``data/README.md``.
"""

from . import paths
from .paths import data_root, processed_dir, resolve
from .onephoton import *  # noqa: F401,F403
from .behavior_analysis import *  # noqa: F401,F403
from .trace_analysis_functions import *  # noqa: F401,F403
