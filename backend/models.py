from typing import Any

from django.db import models

class User(models.Model):
    """
    Adding user table to store user data.
    """
    ROLE_CHOICES = [
        ("Admin", "Admin"), ("User", "User")
    ]

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64)
    email = models.EmailField(max_length=128)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Workflow(models.Model):
    """
    Storing all workflows' metadata.
    """
    STATUS_CHOICES = [
        ("Active", "Active"), ("Pending", "Pending"), ("Rejected", "Rejected")
    ]

    workflow_id = models.AutoField(primary_key=True)
    workflow_name = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    root_template_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.workflow_name

class Templates(models.Model):
    """
    Storing all templates metadata fetched from WhatsApp Business API
    """
    template_id = models.AutoField(primary_key=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="templates")
    template_name = models.CharField(max_length=128)
    template_category = models.CharField(max_length=128)
    template_content = models.TextField()
    template_params = models.JSONField()
    template_status = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.template_name

class WorkflowMapping(models.Model):
    """
    storing all workflow details
    """
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="mappings")
    template = models.ForeignKey(Templates, on_delete=models.CASCADE)
    parent_mapping = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_mappings")
    is_root = models.BooleanField(default=False)
    template_sequence_order = models.IntegerField()
    condition_trigger = models.CharField(max_length=255, blank=True, default="")
    template_params = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class APILog(models.Model):
    """
    Storing all workflows report
    """
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="logs")
    node_id = models.ForeignKey(WorkflowMapping, on_delete=models.CASCADE)
    template = models.ForeignKey(Templates, on_delete=models.CASCADE)
    request_payload = models.JSONField()
    response_code = models.IntegerField()
    response_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)