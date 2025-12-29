import pytest
import json
from django.urls import reverse

from backend.models import WorkflowMapping
from tests.fixtures.edit_workflow import workflow_with_mappings
from tests.fixtures.update_workflow import update_workflow_payload

@pytest.mark.django_db
class TestUpdateWorkflowPUT:
    def test_update_workflow_success(self, client, workflow_with_mappings, update_workflow_payload):
        workflow = workflow_with_mappings
        url = reverse("update-workflow", args = [workflow.workflow_id])

        response = client.put(
            url,
            data = json.dumps(update_workflow_payload),
            content_type = "application/json",
        )
        body = response.json()

        active_mappings = WorkflowMapping.objects.filter(workflow=workflow, is_active=True)

        assert response.status_code == 200
        assert body["response"] == "workflow updated successfully"

        assert WorkflowMapping.objects.filter(workflow=workflow, is_active=False).exists()
        assert active_mappings.count() == 2
        assert active_mappings.filter(is_root=True).count() == 1

    def test_invalid_payload(self, client, workflow_with_mappings):
        workflow = workflow_with_mappings
        url = reverse("update-workflow", args = [workflow.workflow_id])

        response = client.put(url, data = json.dumps({}), content_type = "application/json")

        assert response.status_code == 400

    def test_update_workflow_not_found(self, client):
        url = reverse("update-workflow", args = [9999])

        response = client.put(url, data = json.dumps({"workflow_name": "X"}), content_type = "application/json")

        assert response.status_code == 404