import os
import logging
from google.cloud import compute_v1
from flask import render_template_string
from markupsafe import Markup
import vertexai
from vertexai.generative_models import GenerativeModel
import functions_framework
from google.api_core import exceptions
from datetime import datetime
from zoneinfo import ZoneInfo


def get_vm_data(project_id: str) -> str:
    """Collects VM instance data and returns HTML table with color-coded status."""
    try:
        instances_client = compute_v1.InstancesClient()
        agg_list = instances_client.aggregated_list(project=project_id)

        # Start HTML table
        table_html = """
        <table style="width:100%; border-collapse: collapse;">
          <thead>
            <tr style="background-color: #f1f1f1;">
              <th style="border: 1px solid #ddd; padding: 8px;">Instance</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Machine Type</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Region / Zone</th>
              <th style="border: 1px solid #ddd; padding: 8px;">Creation Time</th>
              <th style="border: 1px solid #ddd; padding: 8px;">State</th>
            </tr>
          </thead>
          <tbody>
        """

        has_instances = False
        for zone, response in agg_list:
            if response.instances:
                has_instances = True
                zone_name = zone.split("/")[-1]
                for instance in response.instances:
                    # Color code status
                    status = instance.status
                    if status == "RUNNING":
                        color = "green"
                    elif status == "TERMINATED":
                        color = "red"
                    elif status in ["PROVISIONING", "STOPPING", "STAGING"]:
                        color = "orange"
                    else:
                        color = "black"

                    table_html += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">{instance.name}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{instance.machine_type.split('/')[-1]}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{zone_name}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{instance.creation_timestamp}</td>
                        <td style="border: 1px solid #ddd; padding: 8px; color:{color}; font-weight:bold;">{status}</td>
                    </tr>
                    """

        if not has_instances:
            table_html += """
            <tr>
                <td colspan="5" style="border: 1px solid #ddd; padding: 8px; text-align:center;">
                    No VM instances found.
                </td>
            </tr>
            """

        table_html += "</tbody></table>"
        return table_html

    except exceptions.GoogleAPICallError as e:
        logging.error(f"VM fetch error: {e}")
        return "<b>Error:</b> Could not fetch VM data."

def get_ai_advice(project_id: str, region: str, vms_text: str) -> str:
    try:
        vertexai.init(project=project_id, location=region)
        model = GenerativeModel("gemini-2.0-flash-lite")

        clean_vms = vms_text.replace("<br>", "\n")

        prompt = f"""
You are a GCP cost optimization assistant.

Project: {project_id}

VM summary:
{clean_vms}

Give short, actionable cost optimization advice.
Format using HTML (<ul>, <li>, <b>).
Do NOT include <html> or <body>.
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        logging.error(f"Vertex AI error: {e}")
        return "<b>Error:</b> AI recommendations unavailable."


def render_html(project_id, vms_text, advice_html, paris_time, user_name, user_email):
    try:
        with open("index.html") as f:
            template = f.read()

        return render_template_string(
            template,
            project_id=project_id,
            user_name=user_name,
            user_email=user_email,
            vms_text=Markup(vms_text),
            advice_html=Markup(advice_html),
            paris_time=paris_time
        )
    except Exception as e:
        logging.error(f"Template error: {e}")
        return "Template rendering error", 500



@functions_framework.http
def monitor_gcp(request):
    project_id = os.getenv("GCP_PROJECT")
    region = os.getenv("GCP_REGION", "us-central1")
    USER_NAME = os.getenv("USER_NAME", "Cloud User")
    USER_EMAIL= os.getenv("USER_EMAIL", "")

    if not project_id:
        return "GCP_PROJECT env var missing", 500

    vms_text = get_vm_data(project_id)
    advice_html = get_ai_advice(project_id, region, vms_text)
    # Get current Paris time
    paris_time = datetime.now(
        ZoneInfo("Europe/Paris")
    ).strftime("%A %d %B %Y • %H:%M %Z")

    return render_html(
        project_id,
        vms_text,
        advice_html,
        paris_time,
        USER_NAME,
        USER_EMAIL
    )
