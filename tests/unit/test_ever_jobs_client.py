from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.services.ever_jobs_client import EverJobsApiError, EverJobsClient


def mock_http_client(monkeypatch, *, json_data=None, post_error=None, status_error=None):
    response = MagicMock()
    response.json.return_value = json_data
    if status_error is not None:
        response.raise_for_status.side_effect = status_error

    client = MagicMock()
    client.post = AsyncMock(side_effect=post_error)
    if post_error is None:
        client.post.return_value = response

    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=client)
    context.__aexit__ = AsyncMock(return_value=None)
    constructor = MagicMock(return_value=context)
    monkeypatch.setattr(
        "app.services.ever_jobs_client.httpx.AsyncClient", constructor
    )
    return constructor, client


@pytest.mark.asyncio
async def test_request_uses_endpoint_and_actual_graphql_fields(monkeypatch):
    constructor, http_client = mock_http_client(
        monkeypatch,
        json_data={"data": {"searchJobs": {"jobs": []}}},
    )
    client = EverJobsClient("https://api.example.test/graphql")

    await client.search_jobs(
        "python", results_wanted=7, sites=["DOU", "DJINNI"], dedup=False
    )

    constructor.assert_called_once_with(timeout=60.0)
    call = http_client.post.await_args
    assert call.args[0] == "https://api.example.test/graphql"
    assert call.kwargs["json"]["variables"]["input"] == {
        "searchTerm": "python",
        "resultsWanted": 7,
        "siteType": ["DOU", "DJINNI"],
        "dedup": False,
    }


@pytest.mark.asyncio
async def test_success_returns_jobs(monkeypatch):
    jobs = [{"id": "dou-1", "title": "Python Developer"}]
    mock_http_client(
        monkeypatch,
        json_data={"data": {"searchJobs": {"jobs": jobs}}},
    )

    assert await EverJobsClient("https://api.test/graphql").search_jobs(
        "python"
    ) == jobs


@pytest.mark.asyncio
async def test_graphql_errors_raise_domain_error(monkeypatch):
    mock_http_client(
        monkeypatch,
        json_data={"errors": [{"message": "GraphQL failed"}]},
    )

    with pytest.raises(EverJobsApiError, match="GraphQL failed"):
        await EverJobsClient("https://api.test/graphql").search_jobs("python")


@pytest.mark.asyncio
async def test_http_status_error_raises_domain_error(monkeypatch):
    request = httpx.Request("POST", "https://api.test/graphql")
    response = httpx.Response(500, request=request)
    mock_http_client(
        monkeypatch,
        json_data={},
        status_error=httpx.HTTPStatusError(
            "server error", request=request, response=response
        ),
    )

    with pytest.raises(EverJobsApiError):
        await EverJobsClient("https://api.test/graphql").search_jobs("python")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        httpx.ReadTimeout("timed out"),
        httpx.ConnectError("connection refused"),
    ],
)
async def test_transport_errors_raise_domain_error(monkeypatch, error):
    mock_http_client(monkeypatch, post_error=error)

    with pytest.raises(EverJobsApiError):
        await EverJobsClient("https://api.test/graphql").search_jobs("python")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": {"searchJobs": {"jobs": {"id": "not-a-list"}}}},
    ],
)
async def test_malformed_response_structure_raises_domain_error(
    monkeypatch, payload
):
    mock_http_client(monkeypatch, json_data=payload)

    with pytest.raises(EverJobsApiError):
        await EverJobsClient("https://api.test/graphql").search_jobs("python")
