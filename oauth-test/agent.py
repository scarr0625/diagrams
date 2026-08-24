import os
import httpx

from google.adk.agents import Agent
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import (
    GcpAuthProvider,
    GcpAuthProviderScheme,
)
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_tool import AuthConfig
from google.adk.tools.authenticated_function_tool import (
    AuthenticatedFunctionTool,
)


PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get(
    "GOOGLE_CLOUD_LOCATION",
    "us-east1",
)

AUTH_PROVIDER_NAME = "google-3lo-poc"


# Let ADK use Google Agent Identity Auth Manager
CredentialManager.register_auth_provider(
    GcpAuthProvider()
)


google_auth_config = AuthConfig(
    auth_scheme=GcpAuthProviderScheme(
        name=(
            f"projects/{PROJECT_ID}"
            f"/locations/{LOCATION}"
            f"/authProviders/{AUTH_PROVIDER_NAME}"
        ),

        # Permissions requested from the user
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],

        # Where the UI continues after consent
        continue_uri=(
            "http://localhost:8501/validateUserId"
        ),
    )
)


async def who_am_i(
    credential: AuthCredential,
) -> dict:

    token = None

    if credential.http and credential.http.credentials:
        token = credential.http.credentials.token

    if not token:
        return {
            "success": False,
            "error": "No delegated OAuth token available"
        }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        response.raise_for_status()

        data = response.json()

    return {
        "success": True,
        "email": data.get("email"),
        "name": data.get("name"),
        "subject": data.get("sub"),
    }


who_am_i_tool = AuthenticatedFunctionTool(
    func=who_am_i,
    auth_config=google_auth_config,
)


root_agent = Agent(
    name="three_lo_test_agent",
    model="gemini-2.5-flash",
    instruction="""
You are testing delegated Google OAuth authorization.

If the user asks who they are or asks to test OAuth,
always call the who_am_i tool.

Return the email address reported by the tool.
""",
    tools=[
        who_am_i_tool
    ],
)