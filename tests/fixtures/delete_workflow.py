import pytest
from backend.models import Workflow, Templates, WorkflowMapping

@pytest.fixture
def workflow_with_mappings():
    workflow = Workflow.objects.create(
        workflow_name="WF_Delete",
        status="pending",
        root_template_id=0,
        is_active=True,
    )

    t1 = Templates.objects.create(
        workflow=workflow,
        template_name="welcome",
        template_category="imported",
        template_content="{}",
        template_params={},
        template_status="Imported",
        is_active=True,
    )

    m1 = WorkflowMapping.objects.create(
        workflow=workflow,
        template=t1,
        is_root=True,
        template_sequence_order=1,
        is_active=True,
    )

    workflow.root_template_id = t1.template_id
    workflow.save()

    return workflow
