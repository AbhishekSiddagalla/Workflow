import pytest
from backend.models import User


@pytest.fixture
def test_user(db):
    return User.objects.create(
        username="test_user",
        email="tests@example.com",
        password="pass"
    )


@pytest.fixture
def valid_workflow_payload():
    return {
        "workflow_name": "TestWF",
        "nodes": [
            {
                "client_node_id": "n1",
                "template_name": "temp1",
                "template_payload": {},
                "buttons": [],
                "order": 1,
                "next_node_client_id": "n2"
            },
            {
                "client_node_id": "n2",
                "template_name": "temp2",
                "template_payload": {},
                "buttons": [],
                "order": 2,
                "next_node_client_id": None
            },
        ],
    }


@pytest.fixture
def empty_payload():
    return {
        "workflow_name": "EmptyWorkflow",
        "nodes": []
    }


@pytest.fixture
def missing_target_payload():
    return {
        "workflow_name": "MissingTargetWF",
        "nodes": [
            {
                "client_node_id": "n1",
                "template_name": "temp1",
                "template_payload": {},
                "buttons": [],
                "order": 1,
                "next_node_client_id": None
            }
        ]
    }


@pytest.fixture
def malformed_payload():
    return {
        "workflow_name": 123,
        "nodes": "invalid_type"
    }
