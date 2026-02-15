"""Gemini API補正機能のテスト"""
import pytest
from config.settings import config
from model.gemini import correct_with_gemini


pytestmark = pytest.mark.skipif(
    not config.gemini_api_key,
    reason="GEMINI_API_KEY が設定されていません",
)


@pytest.mark.parametrize(
    "input_text, expected_keywords",
    [
        ("ぱいそんでじぇそんをぱーすする", ["Python", "JSON"]),
        ("りあくとのゆーずえふぇくとふっくをつかう", ["React", "useEffect"]),
        ("どっかーこんてなをきどうする", ["Docker"]),
        ("じっと こみっと でへんこうをほぞんする", ["git", "commit"]),
    ],
)
def test_correct_with_gemini(input_text: str, expected_keywords: list[str]) -> None:
    """Geminiがプログラミング用語を正しく補正するか"""
    result = correct_with_gemini(input_text)
    for keyword in expected_keywords:
        assert keyword in result, f"'{keyword}' が結果に含まれていない: {result}"


def test_empty_input() -> None:
    """空文字列はそのまま返す"""
    assert correct_with_gemini("") == ""
    assert correct_with_gemini("   ") == "   "
