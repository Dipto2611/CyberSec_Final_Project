"""Lightweight Day 3 tests for the reusable text preprocessor."""

from src.preprocessing import TextPreprocessor


def processor() -> TextPreprocessor:
    return TextPreprocessor()


def test_empty_string_returns_empty_string() -> None:
    assert processor().preprocess_text("") == ""


def test_missing_input_returns_empty_string() -> None:
    assert processor().preprocess_text(None) == ""


def test_whitespace_only_returns_empty_string() -> None:
    assert processor().preprocess_text(" \t\n ") == ""


def test_url_is_preserved_as_security_token() -> None:
    result = processor().preprocess_text("Visit https://example.com/login now")
    assert "urltoken" in result
    assert "urldomain" in result
    assert "exampl" in result


def test_email_is_preserved_as_security_token() -> None:
    result = processor().preprocess_text("Contact analyst@example.com")
    assert "emailtoken" in result
    assert "exampl" in result


def test_numbers_become_explicit_marker() -> None:
    assert "numtoken" in processor().preprocess_text("Pay 2500 rupees by 2026")


def test_punctuation_only_becomes_empty() -> None:
    assert processor().preprocess_text("!!! ??? ... --- ___") == ""


def test_mixed_case_is_normalized() -> None:
    assert processor().preprocess_text("URGENT Verify ACCOUNT") == "urgent verifi account"


def test_unicode_text_is_retained() -> None:
    result = processor().preprocess_text("Café सुरक्षा")
    assert "café" in result
    assert "सुरक्षा" in result


def test_realistic_phishing_message_keeps_threat_signals() -> None:
    result = processor().preprocess_text(
        "URGENT: verify your bank account at https://secure-example.com/login "
        "or it will be suspended."
    )
    assert "urgent" in result
    assert "verifi" in result
    assert "bank" in result
    assert "urltoken" in result

