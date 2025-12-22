import pytest
from backend.models import Workflow

@pytest.fixture
def active_workflows(db):
    return [
        Workflow.objects.create(
            workflow_name = "WF 1",
            status = "Active",
            is_active = True,
            root_template_id = 0
        ),
        Workflow.objects.create(
            workflow_name="WF 2",
            status="Pending",
            is_active=True,
            root_template_id=0
        )
    ]

@pytest.fixture
def mixed_workflows(db):
    active = Workflow.objects.create(
            workflow_name = "Active WF",
            status = "Active",
            is_active = True,
            root_template_id = 0
        )

    inactive = Workflow.objects.create(
            workflow_name = "Inactive WF",
            status = "Active",
            is_active = False,
            root_template_id = 0
        )
    return active, inactive