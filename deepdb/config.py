import os
import logging
from google.adk.agents.callback_context import CallbackContext
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv
from dataclasses import dataclass, field

import google.auth
from google.auth.credentials import Credentials

logger = logging.getLogger(__name__)


@dataclass
class Config:
  """Configuration class for ADK framework root agent."""

  # Google Cloud Configuration
  project_id: Optional[str] = field(default=None)
  location: Optional[str] = field(default=None)
  dataset: Optional[str] = field(default=None)
  use_vertex_ai: bool = field(default=False)
  connection_id: Optional[str] = field(default=None)

  # Authentication
  credentials: Optional[Credentials] = field(default=None, init=False)
  service_account_path: Optional[str] = field(default=None)

  # Model Configuration
  critic_model: str = field(default="gemini-2.5-pro")
  worker_model: str = field(default="gemini-2.5-flash")
  max_feedback_iterations: int = field(default=2)

  def __post_init__(self):
    """Initialize configuration after dataclass creation."""
    self._load_environment()
    self._initialize_authentication()
    self._set_configuration_values()
    self.validate()

  def _load_environment(self):
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
      load_dotenv(env_path)
      logger.info(f"Loaded environment from {env_path}")
    else:
      logger.info("No .env file found, using system environment variables")

  def _initialize_authentication(self) -> Tuple[Optional[Credentials], Optional[str]]:
    """Initialize Google Cloud authentication.

    Priority order:
    1. Service account key file from environment variable
    2. Service account key file from .env
    3. Google Application Default Credentials (ADC)

    Returns:
        Tuple of (credentials, project_id)
    """
    credentials = None
    project_id = None

    # Check for service account key file
    service_account_path = (
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or
            os.getenv("SERVICE_ACCOUNT_KEY_PATH") or
            self.service_account_path
    )

    if service_account_path and os.path.exists(service_account_path):
      try:
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
          service_account_path
        )
        # Get project_id from service account file
        import json
        with open(service_account_path, 'r') as f:
          service_account_info = json.load(f)
          project_id = service_account_info.get('project_id')

        self.service_account_path = service_account_path
        logger.info(f"Using service account credentials from: {service_account_path}")
        logger.info(f"Project ID from service account: {project_id}")

      except Exception as e:
        logger.warning(f"Failed to load service account from {service_account_path}: {e}")
        logger.info("Falling back to Application Default Credentials")

    # Fall back to Application Default Credentials if no service account
    if credentials is None:
      try:
        credentials, adc_project_id = google.auth.default()
        project_id = project_id or adc_project_id
        logger.info("Using Google Application Default Credentials")
        logger.info(f"Project ID from ADC: {adc_project_id}")

      except Exception as e:
        logger.error(f"Failed to initialize any authentication method: {e}")
        raise ValueError(
          "No valid authentication found. Please either:\n"
          "1. Set GOOGLE_APPLICATION_CREDENTIALS to a service account key file path\n"
          "2. Run 'gcloud auth application-default login'\n"
          "3. Ensure you're running on a platform with default credentials (GCE, Cloud Run, etc.)"
        )

    self.credentials = credentials
    return credentials, project_id

  def _set_configuration_values(self):
    """Set configuration values from environment variables with fallbacks."""
    # Get project ID from multiple sources with priority
    _, auth_project_id = self._initialize_authentication()
    self.project_id = (
            os.getenv("GOOGLE_CLOUD_PROJECT") or
            os.getenv("GCP_PROJECT_ID") or
            auth_project_id
    )

    self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-east1").lower()
    self.dataset = os.getenv("GOOGLE_BQ_DATASET", "kaggle_BQ_AI")
    self.use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
    self.connection_id = os.getenv("GOOGLE_BQ_CONNECTION_ID")

    # Model configuration
    self.critic_model = os.getenv("CRITIC_MODEL", os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-pro"))
    self.worker_model = os.getenv("WORKER_MODEL", os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"))

    # Convert max_feedback_iterations to int with error handling
    try:
      self.max_feedback_iterations = int(os.getenv("MAX_FEEDBACK_ITERATION", "2"))
    except ValueError:
      logger.warning("Invalid MAX_FEEDBACK_ITERATION value, using default: 2")
      self.max_feedback_iterations = 2

  def initialize_state_vars(self, callback_context: CallbackContext) -> None:
    """Initialize state variables in the callback context.

    Args:
        callback_context: The ADK callback context to initialize
    """
    if not hasattr(callback_context, 'state'):
      logger.error("CallbackContext does not have 'state' attribute")
      return

    try:
      callback_context.state["PROJECT"] = self.project_id
      callback_context.state["BQ_LOCATION"] = self.location
      callback_context.state["BQ_DATASET"] = self.dataset
      callback_context.state["BQ_CONNECTION_ID"] = self.connection_id

      logger.info("Successfully initialized state variables")
    except Exception as e:
      logger.error(f"Failed to initialize state variables: {e}")
      raise

  def validate(self) -> bool:
    """Validate that all required configuration is present.

    Returns:
        bool: True if configuration is valid

    Raises:
        ValueError: If required configuration is missing
    """
    errors = []

    if not self.project_id:
      errors.append("Project ID is required (set GOOGLE_CLOUD_PROJECT or GCP_PROJECT_ID)")

    if not self.location:
      errors.append("Location is required (set GOOGLE_CLOUD_LOCATION)")

    if not self.dataset:
      errors.append("Dataset is required (set GOOGLE_BQ_DATASET)")

    if self.max_feedback_iterations < 1:
      errors.append("max_feedback_iterations must be at least 1")

    if errors:
      error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
      raise ValueError(error_msg)

    logger.info("Configuration validation passed")
    return True

  @property
  def project_location(self) -> str:
    """Get the project location in the format required by BigQuery and Dataform.

    Returns:
        str: Project location in format 'project_id.location'
    """
    return f"{self.project_id}.{self.location}"

  @property
  def vertex_project_location(self) -> str:
    """Get the project location in the format required by Vertex AI.

    Returns:
        str: Project location in format 'project_id.location'
    """
    return f"{self.project_id}.{self.location}"

  def to_dict(self) -> dict:
    """Convert configuration to dictionary for logging/debugging.

    Returns:
        dict: Configuration as dictionary (sensitive values masked)
    """
    return {
      "project_id": self.project_id,
      "location": self.location,
      "dataset": self.dataset,
      "use_vertex_ai": self.use_vertex_ai,
      "connection_id": "***masked***" if self.connection_id else None,
      "service_account_path": "***masked***" if self.service_account_path else None,
      "has_credentials": self.credentials is not None,
      "critic_model": self.critic_model,
      "worker_model": self.worker_model,
      "max_feedback_iterations": self.max_feedback_iterations,
    }

  def __repr__(self) -> str:
    """String representation of configuration."""
    return f"Config({self.to_dict()})"

  def get_credentials(self) -> Credentials:
    """Get the initialized Google Cloud credentials.

    Returns:
        Credentials: Google Cloud credentials object

    Raises:
        ValueError: If credentials are not initialized
    """
    if self.credentials is None:
      raise ValueError("Credentials not initialized. Call _initialize_authentication() first.")
    return self.credentials

  def get_auth_info(self) -> dict:
    """Get information about the current authentication method.

    Returns:
        dict: Authentication information for debugging
    """
    return {
      "has_credentials": self.credentials is not None,
      "using_service_account": self.service_account_path is not None,
      "service_account_path": self.service_account_path,
      "project_id": self.project_id,
    }

def get_config() -> Config:
  """Get or create the configuration singleton.

  Returns:
      Config: The configuration instance
  """
  global _config_instance
  if '_config_instance' not in globals():
    _config_instance = Config()
  return _config_instance

def before_agent_callback(callback_context: CallbackContext):
  """Initialize agent state with configuration values."""
  get_config().initialize_state_vars(callback_context)

CONFIG = get_config()
