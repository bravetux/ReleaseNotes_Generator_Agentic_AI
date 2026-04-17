"""AWS client factory functions for Bedrock and other AWS services."""

import boto3

from release_notes_agent.config.settings import settings


def get_bedrock_session() -> boto3.Session:
    """Return a boto3 Session with credentials for Bedrock.

    Supports temporary credentials (AWS_SESSION_TOKEN) for SSO / STS.
    """
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.aws_session_token:
        kwargs["aws_session_token"] = settings.aws_session_token
    return boto3.Session(**kwargs)


def get_aws_client(service: str):
    """Return a boto3 client for the given AWS service.

    All tools should use this factory — never call boto3.client() directly.
    """
    return boto3.client(service, region_name=settings.aws_region)
