"""Gemini API補正機能のテスト"""
import pytest
from app.config import config
from app.gemini import GeminiCorrector


pytestmark = pytest.mark.skipif(
    not config.gemini_api_key,
    reason="GEMINI_API_KEY が設定されていません",
)

gemini = GeminiCorrector()


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
    result = gemini.correct(input_text)
    for keyword in expected_keywords:
        assert keyword in result, f"'{keyword}' が結果に含まれていない: {result}"


def test_empty_input() -> None:
    """空文字列はそのまま返す"""
    assert gemini.correct("") == ""
    assert gemini.correct("   ") == "   "
