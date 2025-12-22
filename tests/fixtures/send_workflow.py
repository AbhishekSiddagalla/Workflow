import pytest
from backend.models import Workflow, Templates, WorkflowMapping

@pytest.fixture
def workflow_with_root_node():
    workflow = Workflow.objects.create(
        workflow_name="Main WF",
        status="Active",
        is_active=True,
        root_template_id=0
    )

    root_template = Templates.objects.create(
        workflow=workflow,
        template_name="welcome",
        template_params={
            "components": [
                {
                    "type": "buttons",
                    "buttons": [
                        {"id": "menu", "title": "Menu"},
                        {"id": "available_services", "title": "Available Services"}
                    ]
                }
            ]
        },
        is_active=True
    )

    root_node = WorkflowMapping.objects.create(
        workflow=workflow,
        template=root_template,
        is_root=True,
        is_active=True,
        template_sequence_order = 1
    )

    return workflow, root_node


@pytest.fixture
def nested_workflow_nodes(workflow_with_root):
    workflow, root_node = workflow_with_root

    menu_template = Templates.objects.create(
        workflow=workflow,
        template_name="menu_template",
        template_params={"components": []},
        is_active=True
    )

    services_template = Templates.objects.create(
        workflow=workflow,
        template_name="services_template",
        template_params={"components": []},
        is_active=True
    )

    menu_node = WorkflowMapping.objects.create(
        workflow=workflow,
        template=menu_template,
        parent_mapping=root_node,
        condition_trigger="menu",
        is_active=True
    )

    services_node = WorkflowMapping.objects.create(
        workflow=workflow,
        template=services_template,
        parent_mapping=root_node,
        condition_trigger="available_services",
        is_active=True
    )

    return workflow, root_node, menu_node, services_node

@pytest.fixture
def broken_workflow():
    return Workflow.objects.create(
        workflow_name = "Broken Workflow",
        status = "Active",
        is_active = True,
        root_template_id = 0
    )
