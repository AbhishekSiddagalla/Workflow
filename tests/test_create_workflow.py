import json
import pytest
from django.urls import reverse
from django.test import Client
from backend.models import Workflow, Templates, WorkflowMapping

from .fixtures import test_user, valid_workflow_payload, empty_payload, missing_target_payload, malformed_payload


@pytest.mark.django_db(transaction=True)
class TestCreateWorkflowPOST:

    def setup_method(self):
        self.client = Client()
        self.url = reverse("all-workflows")

    def test_successful_workflow_creation(self, test_user, valid_workflow_payload):
        response = self.client.post(
            self.url,
            data=json.dumps(valid_workflow_payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        res = response.json()
        assert "workflow_id" in res

        workflow = Workflow.objects.get(pk=res["workflow_id"])
        assert workflow.workflow_name == valid_workflow_payload["workflow_name"]
        assert workflow.status == "pending"

        assert Templates.objects.filter(workflow=workflow).count() == len(valid_workflow_payload["nodes"])
        assert WorkflowMapping.objects.filter(workflow=workflow).count() == len(valid_workflow_payload["nodes"])
        assert workflow.root_template_id != 0

    def test_empty_nodes_payload(self, empty_payload):
        response = self.client.post(
            self.url,
            data=json.dumps(empty_payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        res = response.json()

        workflow = Workflow.objects.get(pk=res["workflow_id"])
        assert workflow.workflow_name == "EmptyWorkflow"
        assert Templates.objects.filter(workflow=workflow).count() == 0
        assert WorkflowMapping.objects.filter(workflow=workflow).count() == 0
        assert workflow.root_template_id == 0

    def test_missing_target_node_mapping(self, missing_target_payload):
        response = self.client.post(
            self.url,
            data=json.dumps(missing_target_payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        res = response.json()

        workflow = Workflow.objects.get(pk=res["workflow_id"])

        mappings = WorkflowMapping.objects.filter(workflow=workflow)
        assert mappings.count() == 1

        mapping = mappings.first()
        assert mapping.parent_mapping is None
        assert mapping.is_root is True

    def test_malformed_payload(self, malformed_payload):
        response = self.client.post(
            self.url,
            data=json.dumps(malformed_payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        res = response.json()
        assert "Error" in res
        assert res["Error"] == "Invalid payload"
        assert "details" in res

    def test_template_and_mapping_creation_logic(self, test_user):
        payload = {
            "workflow_name": "WF_Test",
            "nodes": [
                {
                    "client_node_id": "n1",
                    "label": "Start",
                    "template_name": "t1",
                    "template_payload": {"msg": "hello"},
                    "template_params": {"a": 1},
                    "buttons": [],
                    "order": 1
                }
            ]
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200

        workflow_id = response.json()["workflow_id"]
        workflow = Workflow.objects.get(pk=workflow_id)

        template = Templates.objects.get(workflow=workflow)
        assert template.template_name == "t1"
        assert template.template_params == {"a": 1}

        mapping = WorkflowMapping.objects.get(workflow=workflow)
        assert mapping.template == template
        assert mapping.template_sequence_order == 1
        assert mapping.is_root is True

    def test_parent_child_mapping_assignment(self):
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

        response = self.client.post(
            self.url,
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
