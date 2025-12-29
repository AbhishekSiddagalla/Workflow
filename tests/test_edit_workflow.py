import pytest
from django.urls import reverse

from tests.fixtures.edit_workflow import workflow_with_mappings

@pytest.mark.django_db
class TestFetchWorkflowForEditGET:
    def test_fetch_workflow_success(self, client, workflow_with_mappings):
        workflow = workflow_with_mappings
        url = reverse("edit-workflow", args=[workflow.workflow_id])

        response = client.get(url)
        body = response.json()

        assert response.status_code == 200
        assert body["workflow_id"] == workflow.workflow_id
        assert body["workflow_name"] == workflow.workflow_name

        assert "nodes" in body
        assert "edges" in body
        assert len(body["nodes"]) == 1

    def test_workflow_not_found(self, client):
        url = reverse("edit-workflow", args=[0000])
        response = client.get(url)

        assert response.status_code == 404