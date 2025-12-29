import json
import pytest
from django.urls import reverse
from backend.models import Workflow, Templates, WorkflowMapping

from tests.fixtures.create_workflow import test_user, valid_workflow_payload, empty_payload, missing_target_payload, malformed_payload


@pytest.mark.django_db(transaction=True)
class TestCreateWorkflowPOST:
    def test_successful_workflow_creation(self, client, valid_workflow_payload):
        url = reverse("all-workflows")
        response = client.post(
            url,
            data=json.dumps(valid_workflow_payload),
            content_type="application/json"
        )
        res = response.json()
        workflow = Workflow.objects.get(pk=res["workflow_id"])

        assert response.status_code == 200
        assert "workflow_id" in res

        assert workflow.workflow_name == valid_workflow_payload["workflow_name"]
        assert workflow.status == "pending"

        assert WorkflowMapping.objects.filter(workflow=workflow).count() == len(valid_workflow_payload["nodes"])
        assert workflow.root_template_id != 0

    def test_empty_nodes_payload(self, client, empty_payload):
        url = reverse("all-workflows")
        response = client.post(
            url,
            data=json.dumps(empty_payload),
            content_type="application/json"
        )
        res = response.json()
        workflow = Workflow.objects.get(pk=res["workflow_id"])

        assert response.status_code == 200

        assert workflow.workflow_name == "EmptyWorkflow"

        assert WorkflowMapping.objects.filter(workflow=workflow).count() == 0
        assert workflow.root_template_id == 0

    def test_missing_target_node_mapping(self, client, missing_target_payload):
        url = reverse("all-workflows")
        response = client.post(
            url,
            data=json.dumps(missing_target_payload),
            content_type="application/json"
        )
        res = response.json()
        workflow = Workflow.objects.get(pk=res["workflow_id"])
        mappings = WorkflowMapping.objects.filter(workflow=workflow)
        mapping = mappings.first()

        assert mapping.parent_mapping is None
        assert mapping.is_root is True

    def test_malformed_payload(self, client, malformed_payload):
        url = reverse("all-workflows")
        response = client.post(
            url,
            data=json.dumps(malformed_payload),
            content_type="application/json"
        )
        res = response.json()

        assert response.status_code == 400
        assert "Error" in res
        assert res["Error"] == "Invalid payload"


    def test_parent_child_mapping_assignment(self, client):
        url = reverse("all-workflows")
        payload = {
            "workflow_name": "WF_ParentChild",
            "nodes": [
                {
                    "client_node_id": "n1",
                    "template_name": "t1",
                    "template_payload": {},
                    "buttons": [
                        {"id": "b1", "title": "Go", "next_node_client_id": "n2"}
                    ],
                    "order": 1
                },
                {
                    "client_node_id": "n2",
                    "template_name": "t2",
                    "template_payload": {},
                    "buttons": [],
                    "order": 2
                }
            ]
        }

        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200

        workflow_id = response.json()["workflow_id"]
        workflow = Workflow.objects.get(pk=workflow_id)

        m1 = WorkflowMapping.objects.get(workflow=workflow, template__template_name="t1")
        m2 = WorkflowMapping.objects.get(workflow=workflow, template__template_name="t2")

        assert m2.parent_mapping == m1
        assert m1.is_root is True
        assert m2.is_root is False


    def test_duplicate_workflow_name(self, client, valid_workflow_payload):
        url = reverse("all-workflows")

        client.post(url, data=json.dumps(valid_workflow_payload), content_type="application/json")
        response = client.post(url, data=json.dumps(valid_workflow_payload), content_type="application/json")

        assert response.status_code == 409

    def test_duplicate_client_node_id(self, client):
        url = reverse("all-workflows")

        payload = {
            "workflow_name": "WF_DuplicateNodeId",
            "nodes": [
                {"client_node_id": "n1", "template_name": "t1"},
                {"client_node_id": "n1", "template_name": "t2"}
            ]
        }

        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400

    def test_multiple_root_nodes_created(self, client):
        url = reverse("all-workflows")

        payload = {
            "workflow_name": "WF_MultiRoot",
            "nodes": [
                {"client_node_id": "n1", "template_name": "t1", "buttons": []},
                {"client_node_id": "n2", "template_name": "t2", "buttons": []},
            ]
        }

        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        workflow = Workflow.objects.get(pk=response.json()["workflow_id"])
        roots = WorkflowMapping.objects.filter(workflow=workflow, is_root=True)

        assert roots.count() == 1

    def test_button_points_to_unknown_node(self, client):
        url = reverse("all-workflows")

        payload = {
            "workflow_name": "WF_InvalidEdge",
            "nodes": [
                {
                    "client_node_id": "n1",
                    "template_name": "t1",
                    "buttons": [
                        {"id": "b1", "next_node_client_id": "n999"}
                    ]
                }
            ]
        }

        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
