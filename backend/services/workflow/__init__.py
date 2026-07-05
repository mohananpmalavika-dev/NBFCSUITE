"""
Workflow Engine Service Module

This module provides comprehensive workflow management functionality for the NBFC platform.

Services:
- Template Service: Workflow template management and validation
- Execution Service: Workflow instance execution and state management
- Task Service: User task management and operations

Routers:
- Template Router: Template CRUD and validation endpoints
- Instance Router: Workflow lifecycle and monitoring endpoints
- Task Router: Task management and operations endpoints

All services follow multi-tenant architecture with complete audit trails.
"""

from .template_service import WorkflowTemplateService
from .execution_service import WorkflowExecutionService
from .task_service import WorkflowTaskService
from .template_router import router as template_router
from .instance_router import router as instance_router
from .task_router import router as task_router

__all__ = [
    "WorkflowTemplateService",
    "WorkflowExecutionService",
    "WorkflowTaskService",
    "template_router",
    "instance_router",
    "task_router",
]
