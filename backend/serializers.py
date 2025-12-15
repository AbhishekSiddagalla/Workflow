from rest_framework import serializers

class ButtonSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    next_node_client_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

class NodeSerializer(serializers.Serializer):
    client_node_id = serializers.CharField()
    label = serializers.CharField(required=False, allow_blank=True)
    template_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    template_payload = serializers.JSONField(required=False, allow_null=True)
    template_params = serializers.JSONField(required=False, allow_null=True)
    buttons = ButtonSerializer(many=True, required=False)
    position = serializers.DictField(child=serializers.FloatField(), required=False)
    order = serializers.IntegerField(required=False)

class CreateWorkflowSerializer(serializers.Serializer):
    workflow_name = serializers.CharField()
    nodes = NodeSerializer(many=True, required=False)