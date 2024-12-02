from jinja2 import Environment, FileSystemLoader, select_autoescape
import os


TEMPLATES_FOLDER = "api/utils/celery_setup/templates/"

print(f"Template folder: {TEMPLATES_FOLDER}")

email_templates = Environment(
    loader=FileSystemLoader(TEMPLATES_FOLDER),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)

def get_template(template_name: str):
    """
    Retrieves a template by name, handling missing template errors gracefully.
    """
    try:
        return email_templates.get_template(template_name)
    except Exception as e:
        print(f"Error loading template '{template_name}': {e}")
        raise ValueError(f"Template '{template_name}' not found.")


def render_template(template_name: str, context: dict):
    """
    Renders a template with the provided context data.

    Args:
        template_name (str): Name of the template file.
        context (dict): Dictionary with context data for rendering.

    Returns:
        str: The rendered HTML content.
    """
    template = get_template(template_name)
    return template.render(context)
