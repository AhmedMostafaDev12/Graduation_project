"""
External Integrations
=====================

This module handles integrations with external systems:
- task_database_integration.py: Integrates with your backend task database
"""

from .task_database_integration import (
    TaskDatabaseService,
    get_complete_user_context,
    Task,
    QualitativeDataEntry
)

__all__ = [
    'TaskDatabaseService',
    'get_complete_user_context',
    'Task',
    'QualitativeDataEntry',
]
