"""
Dialog classes for the Laboratory TAT Analysis Application.
"""
from .base_dialogs import (
    BaseDialog, TitleInputDialog, AdjustTimeDialog, 
    AddParameterDialog, DebugDialog, ScenarioAnalysisDialog
)
from .selection_dialogs import MultiSelectDialog, StatisticsSelectionDialog
from .help_dialog import HelpDialog
from .correction_details_dialog import CorrectionDetailsDialog