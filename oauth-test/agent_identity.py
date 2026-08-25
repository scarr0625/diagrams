@app.post("/agent-identity/finalize")
async def finalize_agent_identity_credentials(
    req: FinalizeAgentIdentityCredentialsRequest,
) -> dict[str, str]:

    try:
        from google.api_core.client_options import ClientOptions
        from google.api_core.exceptions import GoogleAPICallError
        from google.api_core.exceptions import InvalidArgument

        from google.cloud.agentidentitycredentials_v1 import (
            AuthProviderCredentialsServiceClient,
            FinalizeCredentialsRequest,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Agent Identity support requires: "
                'pip install "google-adk[agent-identity]"'
            ),
        ) from e

    # ADK Web may still send connector_name.
    # Normalize legacy callback resource to the new resource.
    auth_provider_name = req.connector_name.replace(
        "/connectors/",
        "/authProviders/",
    )

    client_options = None

    if host := os.environ.get(
        "AGENT_IDENTITY_CREDENTIALS_TARGET_HOST"
    ):
        client_options = ClientOptions(
            api_endpoint=host
        )

    client = AuthProviderCredentialsServiceClient(
        client_options=client_options,
        transport="rest",
    )

    try:
        state_bytes = base64.urlsafe_b64decode(
            req.user_id_validation_state
            + "=" * (-len(req.user_id_validation_state) % 4)
        )
    except (binascii.Error, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid base64 user_id_validation_state: {e}",
        ) from e

    finalize_request = FinalizeCredentialsRequest(
        auth_provider=auth_provider_name,
        user_id=req.user_id,
        user_id_validation_state=state_bytes,
        consent_nonce=req.consent_nonce,
    )

    try:
        await asyncio.to_thread(
            client.finalize_credentials,
            finalize_request,
        )

    except InvalidArgument as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid credentials request: {e}",
        ) from e

    except GoogleAPICallError as e:
        logger.error(
            "API error during Agent Identity finalization: %s",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to finalize credentials: {e}",
        ) from e

    return {"status": "ok"}