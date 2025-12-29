import pytest
from django.urls import reverse

from backend.models import Workflow, WorkflowMapping, Templates, APILog
from tests.fixtures.delete_workflow import workflow_with_mappings

@pytest.mark.django_db
class TestDeleteWorkflowDELETE:
    def test_delete_workflow_success(self, client, workflow_with_mappings):
        workflow = workflow_with_mappings
        url = reverse("delete-workflow", args=[workflow.workflow_id])

        response = client.delete(url)
        body = response.json()

        assert response.status_code == 200
        assert "deleted successfully" in body["response"]

        assert not Workflow.objects.filter(workflow_id = workflow.workflow_id).exists()
        assert not WorkflowMapping.objects.filter(workflow = workflow).exists()
        assert not Templates.objects.filter(workflow = workflow).exists()

    def test_delete_workflow_not_found(self, client):
        url = reverse("delete-workflow", args = [1234])

        response = client.delete(url)

        assert response.status_code == 404

    def test_delete_workflow_without_mappings(self, client):
        workflow = Workflow.objects.create(
            workflow_name = "WF_NoMappings",
            status = "pending",
            root_template_id = 0,
            is_active = True
        )

        url = reverse("delete-workflow", args = [workflow.workflow_id])

        response = client.delete(url)

        assert response.status_code == 200
        assert not Workflow.objects.filter(workflow_id = workflow.workflow_id).exists()

    def test_delete_workflow_multiple_times(self, client, workflow_with_mappings):
        workflow = workflow_with_mappings
        url = reverse("delete-workflow", args=[workflow.workflow_id])

        client.delete(url)
        second_try = client.delete(url)

        assert second_try.status_code == 404