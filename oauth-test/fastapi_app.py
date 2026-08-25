from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
import httpx


@app.get("/validateUserId")
async def validate_user_id(request: Request):

    validation_state = request.query_params.get(
        "user_id_validation_state"
    )

    auth_provider_name = request.query_params.get(
        "auth_provider_name"
    )

    if not validation_state:
        raise HTTPException(
            status_code=400,
            detail="Missing user_id_validation_state",
        )

    if not auth_provider_name:
        raise HTTPException(
            status_code=400,
            detail="Missing auth_provider_name",
        )

    # Retrieve these from the state you stored when ADK
    # originally emitted the credential request.
    user_id = "YOUR_USER_ID"
    consent_nonce = "ORIGINAL_CONSENT_NONCE"

    credentials, _ = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform"
        ]
    )

    credentials.refresh(GoogleAuthRequest())

    finalize_url = (
        "https://agentidentitycredentials.googleapis.com/v1/"
        f"{auth_provider_name}/credentials:finalize"
    )

    payload = {
        "userId": user_id,
        "userIdValidationState": validation_state,
        "consentNonce": consent_nonce,
    }

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            finalize_url,
            json=payload,
            headers=headers,
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=500,
            detail=(
                f"FinalizeCredentials failed: "
                f"{response.status_code} {response.text}"
            ),
        )

    return HTMLResponse("""
        <html>
        <body>
            <h3>Authentication completed.</h3>
            <script>
                setTimeout(() => window.close(), 1000);
            </script>
        </body>
        </html>
    """)