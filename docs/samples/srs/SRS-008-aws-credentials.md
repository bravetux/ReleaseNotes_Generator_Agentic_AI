# SRS-008 — AWS Credentials & Bedrock Client

**Product:** release-notes-agent
**Module:** `config/aws_client.py`, `config/settings.py`
**Target release:** 1.3.0
**Author:** SecEng
**Date:** 2026-04-14

## 1. Overview

Customers authenticate to AWS via a mix of long-lived keys, SSO, and
IAM roles. The current client factory handles static keys well but
leaks behaviour for the other two, and silently logs tokens at debug
level.

## 2. Bugs

- **BUG-8001** — `get_bedrock_session()` logs the full `kwargs` dict at
  DEBUG level, which includes `aws_secret_access_key` and
  `aws_session_token` as plaintext when log level is dialled up for
  troubleshooting.

- **BUG-8002** — If `AWS_DEFAULT_REGION` is not set, boto3 falls back
  to `us-east-1` without warning; customers in EU have hit Bedrock
  endpoint-not-available errors that are hard to diagnose.

- **BUG-8003** — `get_aws_client(service)` never caches the client;
  every tool call constructs a new boto3 client, which costs ~40 ms
  on Windows due to repeated `botocore` shim startup.

## 3. Functional Requirements

- **FR-8001** — Redact `aws_secret_access_key` and `aws_session_token`
  in all log output. Add a unit test that captures log records and
  asserts none of them contain the literal secret value.

- **FR-8002** — At startup, if `aws_region` is empty, raise
  `ConfigError("AWS_DEFAULT_REGION is required")` rather than deferring
  to boto3 defaults.

- **FR-8003** — Memoise clients by service name inside
  `get_aws_client`. Cache must be cleared when credentials are refreshed
  (expose `reset_clients()` for session-token rotation).

- **FR-8004** — Document SSO-based setup in `README.md` with an
  `aws sso login` example and a note on `AWS_PROFILE`.

## 4. Security

Any log redaction regression must fail CI. Secret scanning on `.env`
remains the user's responsibility and is unchanged.
