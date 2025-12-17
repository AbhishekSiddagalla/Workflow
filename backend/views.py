import requests
import json

from django.db import transaction, IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404

from rest_framework import status,permissions
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User, Workflow, Templates, WorkflowMapping, APILog

from .serializers import CreateWorkflowSerializer

from backend.api_config import  api_access_token, api_version, whatsapp_business_account_id, to_phone_number

from backend.services.whatsapp import send_whatsapp_template

class LoginView(APIView):
    """
    POST: { "username": "...", "password": "..." }"
    """
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username: return Response({"error": "username is required"}, status= status.HTTP_400_BAD_REQUEST)
            if not password: return Response({"error": "password is required"}, status= status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)

                return Response({
                    "response": "login successful",
                    "token": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({"error": "No user found"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": "internal server error", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except TokenError: pass

            logout(request)
            return Response({"response": "logout successful"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token: return Response({"error": "token is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)

        except TokenError: return Response({"error": "invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

class DashboardView(APIView):
    def post(self,request):
        return Response({"response": "Welcome to Dashboard"}, status=200)

class FetchAllWorkflowsView(APIView):
    """
    GET /api/workflows/ -> list workflows
    POST /api/workflows/ -> create workflow
    """
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        workflows = Workflow.objects.filter(is_active=True).order_by("-created_at")
        data = [{
            "workflow_id": w.workflow_id,
            "workflow_name": w.workflow_name,
            "status": w.status,
            "created_by": w.created_by.username,
            "created_at": w.created_at
        } for w in workflows]
        return Response({"response": "Workflows Fetched Successfully", "workflows": data}, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        """
        Expected JSON payload:
        {
          "workflow_name": "My workflow",
          "nodes": [
            {
              "client_node_id": "n1",
              "label": "Start Node",
              "template_name": "welcome_template",
              "template_payload": {...},
              "template_params": {...},
              "buttons": [
                {"id": "btn_1", "title": "Yes", "next_node_client_id": "n2"},
                {"id": "btn_2", "title": "No", "next_node_client_id": null}
              ],
              "position": {"x": 100, "y": 200},
              "order": 1
            },
          ]
        }
        """

        serializer = CreateWorkflowSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"Error": "Invalid payload", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        workflow_name = data.get("workflow_name")
        nodes = data.get("nodes") or []

        if Workflow.objects.filter(workflow_name=workflow_name).exists():
            return Response({"Message": "Workflow Name already exists"}, status=status.HTTP_409_CONFLICT)

        try:
            workflow = Workflow.objects.create(
                workflow_name = workflow_name,
                status = "pending",
                root_template_id = 0,
                is_active = True,
            )
        except IntegrityError:
            return Response({"Message": "Workflow Name already exists"}, status=status.HTTP_409_CONFLICT)

        template_map = {} # Template Instance
        mapping_map = {} #Workflowmapping Instance
        for idx, node in enumerate(nodes):
            t_name = node.get("template_name") or None
            payload_json = node.get("template_payload")
            params = node.get("template_params") or {}

            template_obj = None
            if t_name:
                template_obj = template_map.get(t_name)
                if not template_obj:
                    template_obj = Templates.objects.create(
                        workflow = workflow,
                        template_name = t_name,
                        template_category = "imported",
                        template_content = json.dumps(payload_json) if payload_json is not None else "",
                        template_params = params,
                        template_status = "Imported",
                        is_active = True
                    )
                    template_map[t_name] = template_obj

            mapping = WorkflowMapping.objects.create(
                workflow = workflow,
                template = template_obj,
                parent_mapping = None,
                is_root = False,
                template_sequence_order = node.get("order") or (idx+1),
                condition_trigger = "",
                template_params = params or {},
                is_active = True
            )

            client_id = node.get("client_node_id")
            if client_id: mapping_map[client_id] = mapping

        for node in nodes:
            source_client_id = node.get("client_node_id")
            source_mapping = mapping_map.get(source_client_id)
            buttons = node.get("buttons") or []
            for button in buttons:
                next_client_id = button.get("next_node_client_id")
                if next_client_id:
                    target_mapping = mapping_map.get(next_client_id)
                    if target_mapping:
                        if target_mapping.parent_mapping is None:
                            target_mapping.parent_mapping = source_mapping
                            target_mapping.save()

        for client_id, mapping in mapping_map.items():
            if mapping.parent_mapping is None:
                mapping.is_root = True
                mapping.save()

                if workflow.root_template_id == 0 and mapping.template:
                    workflow.root_template_id = mapping.template.template_id
                    workflow.save()

        return Response(
            {"response": "workflow created successfully", "workflow_id": workflow.workflow_id},
            status = status.HTTP_200_OK
        )


class SendWorkflowView(APIView):
    """
    starts workflow by sending root node only
    """
    def post(self, request, w_id):
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response({"Error": "phone_number required"}, status=status.HTTP_400_BAD_REQUEST)

        workflow = get_object_or_404(Workflow, workflow_id=w_id, is_active=True)

        root = workflow.mappings.filter(is_root=True, is_active=True).first()
        if not root or not root.template:
            return Response({"Error": "Root node not configured"}, status=status.HTTP_400_BAD_REQUEST)

        payload, status_code, response_text = send_whatsapp_template(
            phone_number = to_phone_number,
            template_name = root.template.template_name,
            components = root.template.template_params.get("components", [])
        )

        APILog.objects.create(
            user = request.user if request.user.is_authenticated else None,
            workflow = workflow,
            node_id = root,
            template = root.template,
            request_payload = payload,
            response_code = status_code,
            response_message = response_text
        )
        return Response({
            "response": "Workflow started",
            "root_template": root.template.template_name
        }, status=200)

class FetchWorkflowView(APIView):
    def get(self, request, w_id):
        wf = get_object_or_404(Workflow, workflow_id=w_id)
        mappings= wf.mappings.filter(is_active=True).order_by("template_sequence_order")
        data = {
            "workflow_id": wf.workflow_id,
            "workflow_name": wf.workflow_name,
            "status": wf.status,
            "mappings": [
                {
                    "mapping_id": m.id,
                    "template_name": m.template.template_name if m.template else None,
                    "parent_mapping_id": m.parent_mapping.id if m.parent_mapping else None,
                    "order": m.tempate_sequence_order,
                }
                for m in mappings
            ],
        }
        return Response({"response": f"Fetched", "workflow": data}, status=status.HTTP_200_OK)

class UpdateWorkflowView(APIView):
    def put(self, request, id):

        return Response({"response": f" updated successfully"},status=status.HTTP_200_OK)

class DeleteWorkflowView(APIView):
    def delete(self,request):
        workflow_name = None
        return Response({"response": f"{workflow_name} deleted successfully"}, status=status.HTTP_200_OK)

class FetchTemplatesView(APIView):
    # authentication_classes = []
    # permission_classes = []
    def get(self, request):

        url = f"https://graph.facebook.com/{api_version}/{whatsapp_business_account_id}/message_templates"

        headers = {
            "Authorization": f"Bearer {api_access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        templates = response.json().get("data", [])
        return Response({"response": "templates fetched successfully", "templates": templates}, status=status.HTTP_200_OK)

class SyncTemplatesView(APIView):
    def post(self, request):
        return Response({"response": "templates are synced"}, status=status.HTTP_200_OK)

class WhatsAppWebhookView(APIView):
    def post(self, request):
        entry = request.data.get("entry", [])[0]
        changes = entry.get("changes",[])[0]
        value = changes.get("value",{})
        messages = value.get("messages",[])

        if not messages:
            return Response(status= status.HTTP_200_OK)

        message = messages[0]
        phone_number = message["from"]

        button_reply = (
            message.get("interactive", {})
                   .get("buttons", {})
        )

        button_id = button_reply.get("id")
        if not button_id:
            return Response(status=status.HTTP_200_OK)

        last_log = (
            APILog.objects
            .filter(workflow__is_active=True)
            .order_by("-created_at")
            .first()
        )
        if not last_log:
            return Response(status=status.HTTP_200_OK)

        current_node = last_log.node_id

        next_node = current_node.child_mappings.filter(
            condition_trigger = button_id,
            is_active = True
        ).first()

        if not next_node or not next_node.template:
            return Response(status=status.HTTP_200_OK)

        payload, status_code, response_text = send_whatsapp_template(
            phone_number = phone_number,
            template_name = next_node.template.template_name,
            components = next_node.template.template_params.get("components", [])
        )

        APILog.objects.create(
            user = last_log.user,
            workflow = last_log.workflow,
            node_id = next_node,
            template = next_node.template,
            request_payload = payload,
            response_code = status_code,
            response_message = response_text
        )
        return Response(status=status.HTTP_200_OK)