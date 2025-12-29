import pytest

from django.urls import reverse

from  tests.fixtures.fetch_all_workflows import active_workflows, mixed_workflows


@pytest.mark.django_db
class TestFetchAllWorkflowsGET:



    def test_fetch_all_success(self, client, active_workflows):
        url = reverse("all-workflows")

        response = client.get(url)
        body = response.json()
        names = [w["workflow_name"] for w in body["workflows"]]

        assert response.status_code == 200
        assert len(body["workflows"]) == 2
        assert "WF 1" in names
        assert "WF 2" in names

    def test_fetch_all_empty(self, client):
        url = reverse("all-workflows")

        response = client.get(url)
        body = response.json()

        assert response.status_code == 200
        assert body["response"] == "Workflows Fetched Successfully"
        assert body["workflows"] == []

    def test_active_and_inactive_workflows(self, client, mixed_workflows):
        url = reverse("all-workflows")

        response = client.get(url)
        body = response.json()
        names = [w["workflow_name"] for w in body["workflows"]]

        assert "Active WF" in names
        assert "Inactive WF" not in names

    def test_fetch_all_with_required_fields_present(self, client, active_workflows):
        url = reverse("all-workflows")

        response = client.get(url)
        workflows = response.json()["workflows"]

        for w in workflows:
            assert "workflow_id" in w
            assert "workflow_name" in w
            assert "status" in w
            assert "created_at" in w
