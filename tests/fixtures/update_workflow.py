import pytest

@pytest.fixture
def update_workflow_payload():
    return {
        "workflow_name": "Updated Workflow",
        "nodes": [
            {
                "client_node_id": "n1",
                "label": "Start",
                "template_name": "welcome",
                "template_payload": {
                    "type": "body",
                    "text": "Hello user"
                },
                "template_params": {
                    "components": []
                },
                "buttons": [
                    {
                        "id": "btn_yes",
                        "title": "Yes",
                        "next_node_client_id": "n2"
                    }
                ],
                "position": {"x": 200, "y": 100},
                "order": 1
            },
            {
                "client_node_id": "n2",
                "label": "Second",
                "template_name": "followup",
                "template_payload": {
                    "type": "body",
                    "text": "Thanks!"
                },
                "template_params": {
                    "components": []
                },
                "buttons": [],
                "position": {"x": 200, "y": 250},
                "order": 2
            }
        ]
    }
