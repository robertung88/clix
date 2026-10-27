"""Tests for the x-web Relay variable self-healing helpers.

X periodically adds required Relay variables to existing GraphQL operations.
These helpers let the client learn the missing variable from the 422 body and
retry instead of failing the command.
"""

from __future__ import annotations

import json

from clix.core.client import _extract_missing_variable, _guess_missing_variable_value


def _body(variable: str) -> str:
    return json.dumps(
        {
            "errors": [
                {
                    "code": "GRAPHQL_VALIDATION_FAILED",
                    "extensions": {"code": "GRAPHQL_VALIDATION_FAILED"},
                    "message": "must be defined",
                    "path": ["variable", variable],
                }
            ]
        }
    )


class TestExtractMissingVariable:
    def test_reads_name_from_json_string_body(self):
        name = "__relay_internal__pv__xclientsfeaturestweetcomponentsgrokanalyzepostrelayprovider"
        assert _extract_missing_variable(_body(name)) == name

    def test_reads_name_from_dict_body(self):
        assert _extract_missing_variable(json.loads(_body("rest_id"))) == "rest_id"

    def test_returns_none_for_non_validation_error(self):
        body = json.dumps({"errors": [{"code": 88, "message": "Rate limit"}]})
        assert _extract_missing_variable(body) is None

    def test_returns_none_for_unparsable_body(self):
        assert _extract_missing_variable("<html>502</html>") is None
        assert _extract_missing_variable(None) is None


class TestGuessMissingVariableValue:
    def test_relay_provider_flags_are_true(self):
        name = "__relay_internal__pv__sportspostcontextenabledrelayprovider"
        assert _guess_missing_variable_value(name, {}, {}) is True

    def test_rest_id_uses_tweet_id(self):
        assert (
            _guess_missing_variable_value("rest_id", {"tweetId": "123"}, {})
            == "123"
        )

    def test_focal_tweet_id_uses_tweet_id(self):
        assert (
            _guess_missing_variable_value("focalTweetId", {"tweetId": "456"}, {})
            == "456"
        )

    def test_screen_name_uses_legacy_key(self):
        assert (
            _guess_missing_variable_value("screenName", {"screen_name": "x"}, {})
            == "x"
        )

    def test_cursor_defaults_to_none(self):
        assert _guess_missing_variable_value("cursor", {}, {}) is None
