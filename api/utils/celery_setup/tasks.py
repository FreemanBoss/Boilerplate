import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from api.utils.celery_setup.celery_app import app
from api.utils.settings import Config
from api.utils.task_logger import create_logger

RETRY_DELAY = 60  # 60 seconds delay for retry
MAX_RETRIES = 3  # Maximum 3 retries

logger = create_logger("Celery Tasks")


@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
def send_email(self, context: dict):
    """
    Sends email to the user.

    Args:
        context(dict): contains recipient_email, link, subject, and template_name for the email.
    Returns:
        None
    """
    try:
        working_dir = os.getcwd()
        templates_dir = os.path.join(
            working_dir, "api", "utils", "celery_setup", "templates"
        )

        env = Environment(loader=FileSystemLoader(templates_dir))
        try:
            email_template = env.get_template(context.get("template_name"))
        except TemplateNotFound:
            logger.error(
                f"Template '{context.get('template_name')}' not found in {templates_dir}"
            )
            return

        # Render email content
        html = email_template.render(
            {"first_name": context.get("first_name"), "link": context.get("link")}
        )

        # Create the email message
        message = MIMEMultipart("alternative")
        message["Subject"] = context.get("subject")
        message["From"] = Config.MAIL_USERNAME
        message["To"] = context.get("recipient_email")
        part = MIMEText(html, "html")
        message.attach(part)

        with smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.login(
                Config.MAIL_USERNAME,
                Config.MAIL_PASSWORD,
            )
            server.sendmail(
                Config.MAIL_USERNAME,
                context.get("recipient_email"),
                message.as_string(),
            )
            print("email sent to: ", context["recipient_email"])
    except Exception as exc:
        logger.error(f"Email sending failed: {exc}")
        # Retry the task in case of failure
        try:
            raise self.retry(exc=exc, countdown=RETRY_DELAY, max_retries=MAX_RETRIES)
        except self.MaxRetriesExceededError:
            # retry task incase of failure.
            logger.error(f"Max retries exceeded for task {self.request.id}")
