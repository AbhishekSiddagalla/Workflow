import json

import pytest

from django.urls import reverse

from backend.models import APILog
from tests.fixtures.send_workflow import workflow_with_root_node, broken_workflow

@pytest.mark.django_db
class TestSendWorkflowPOST:
    def test_send_workflow_success(self, client, workflow_with_root_node):
        workflow, root_node = workflow_with_root_node
        url = reverse("send-workflow", args = [workflow.workflow_id])

        response = client.post(
            url,
            data = json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )
        body = response.json()
        log = APILog.objects.first()

        assert response.status_code == 200
        assert body["response"] == "Workflow started"
        assert body["root_template"] == root_node.template.template_name

        assert APILog.objects.count() == 1
        assert log.workflow == workflow
        assert log.node_id == root_node
        assert log.template == root_node.template

    def test_phone_number_required(self, client, workflow_with_root_node):
        workflow, root_node = workflow_with_root_node
        url = reverse("send-workflow", args = [workflow.workflow_id])

        response = client.post(url, data = {})

        assert response.status_code == 400
        assert response.json()["Error"] == "phone_number required"

    def test_workflow_not_found(self, client):
        url = reverse("send-workflow", args = [9999])

        response = client.post(
            url,
            data = json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )

        assert response.status_code == 404

    def test_root_node_not_configured(self, client, broken_workflow):
        url = reverse("send-workflow", args = [broken_workflow.workflow_id])

        response = client.post(
            url,
            data = json.dumps({"phone_number": "911234567890"}),
            content_type = "application/json"
         )
        body = response.json()
        assert response.status_code == 400
        assert body["Error"] == "Root node not configured"

    def test_multiple_roots_only_first_used(self, client, workflow_with_root_node):
        workflow, root = workflow_with_root_node

        another = workflow.mappings.exclude(id=root.id).first()
        if another:
            another.is_root = True
            another.save()

        url = reverse("send-workflow", args=[workflow.workflow_id])

        response = client.post(
            url,
            data=json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )

        assert response.status_code == 200

    def test_root_node_inactive(self, client, workflow_with_root_node):
        workflow, root = workflow_with_root_node

        root.is_active = False
        root.save()

        url = reverse("send-workflow", args=[workflow.workflow_id])

        response = client.post(
            url,
            data=json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )

        assert response.status_code == 400
        assert response.json()["Error"] == "Root node not configured"

    def test_api_log_created_only_on_success(self, client, workflow_with_root_node):
        workflow, _ = workflow_with_root_node
        url = reverse("send-workflow", args=[workflow.workflow_id])

        client.post(
            url,
            data=json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )

        assert APILog.objects.count() == 1

    def test_no_root_mapping(self, client, broken_workflow):
        url = reverse("send-workflow", args=[broken_workflow.workflow_id])

        response = client.post(
            url,
            data=json.dumps({"phone_number": "911234567890"}),
            content_type="application/json"
        )

        assert response.status_code == 400
        assert response.json()["Error"] == "Root node not configured"
