import json

import pytest

from django.test import Client
from django.urls import reverse

from backend.models import APILog
from tests.fixtures.send_workflow import workflow_with_root_node, broken_workflow

@pytest.mark.django_db
class TestSendWorkflowPOST:

    def setup_method(self):
        self.client = Client()

    def test_send_workflow_success(self, workflow_with_root_node):
        workflow, root_node = workflow_with_root_node
        url = reverse("send-workflow", args = [workflow.workflow_id])

        response = self.client.post(
            url,
            data = json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )
        body = response.json()
        log = APILog.objects.first()

        assert body["response"] == "Workflow started"
        assert body["root_template"] == "welcome"

        assert APILog.objects.count() == 1
        assert log.workflow == workflow
        assert log.node_id == root_node
        assert log.template == root_node.template

    def test_phone_number_required(self, workflow_with_root_node):
        workflow, root_node = workflow_with_root_node
        url = reverse("send-workflow", args = [workflow.workflow_id])

        response = self.client.post(url, data = {})

        assert response.status_code == 400
        assert response.json()["Error"] == "phone_number required"

    def test_workflow_not_found(self):
        url = reverse("send-workflow", args = [9999])

        response = self.client.post(
            url,
            data = json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )

        assert response.status_code == 404

    def test_root_node_not_configured(self, broken_workflow):
        url = reverse("send-workflow", args = [broken_workflow.workflow_id])

        response = self.client.post(
            url,
            data = json.dumps({"phone_number": "911234567890"}),
            content_type = "application/json"
         )
        body = response.json()
        assert response.status_code == 400
        assert body["Error"] == "Root node not configured"