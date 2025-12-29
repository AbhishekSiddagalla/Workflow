import pytest
from backend.models import Workflow, Templates, WorkflowMapping

@pytest.fixture
def workflow_with_mappings():
    workflow = Workflow.objects.create(
        workflow_name="Test Workflow",
        status="pending",
        root_template_id=0,
        is_active=True
    )

    template = Templates.objects.create(
        workflow=workflow,
        template_name="welcome",
        template_category="imported",
        template_content="{}",
        template_params={},
        template_status="Imported",
        is_active=True
    )

    mapping = WorkflowMapping.objects.create(
        workflow=workflow,
        template=template,
        is_root=True,
        template_sequence_order=1,
        template_params={"position": {"x": 100, "y": 100}},
        is_active=True
    )

    workflow.root_template_id = template.template_id
    workflow.save()

    return workflow
