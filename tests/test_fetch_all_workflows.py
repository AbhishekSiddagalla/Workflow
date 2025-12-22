import pytest
from django.test import Client
from django.urls import reverse

from  tests.fixtures.fetch_all_workflows import active_workflows, mixed_workflows


@pytest.mark.django_db
class TestFetchAllWorkflowsGET:

    def setup_method(self):
        self.client = Client()
        self.url = reverse("all-workflows")

    def test_fetch_all_success(self, active_workflows):
        response = self.client.get(self.url)
        body = response.json()
        names = [w["workflow_name"] for w in body["workflows"]]

        assert response.status_code == 200
        assert len(body["workflows"]) == 2
        assert "WF 1" in names
        assert "WF 2" in names

    def test_fetch_all_empty(self):
        response = self.client.get(self.url)
        body = response.json()

        assert response.status_code == 200
        assert body["response"] == "Workflows Fetched Successfully"
        assert body["workflows"] == []

    def test_active_and_inactive_workflows(self, mixed_workflows):
        response = self.client.get(self.url)
        body = response.json()
        names = [w["workflow_name"] for w in body["workflows"]]

        assert "Active WF" in names
        assert "Inactive WF" not in names