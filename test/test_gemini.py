"""
Gemini API 単体テスト

使用方法:
1. .env ファイルに GEMINI_API_KEY を設定
2. python test_gemini.py を実行
"""
import os
from config.settings import config
from model.gemini import correct_with_gemini


def test_gemini():
    """Gemini API の補正機能をテスト"""

    print("=" * 60)
    print("Gemini API 単体テスト")
    print("=" * 60)

    # 設定確認
    print(f"\n📋 設定:")
    print(f"  GEMINI_MODEL    : {config.gemini_model}")
    print(f"  GEMINI_API_KEY  : {'設定済み' if config.gemini_api_key else '未設定'}")
    print(f"  補正機能        : {'有効' if config.gemini_enabled else '無効'}")

    if not config.gemini_api_key:
        print("\n❌ エラー: GEMINI_API_KEY が設定されていません")
        print("   .env ファイルに GEMINI_API_KEY を設定してください")
        return

    # テストケース
    test_cases = [
        ("ぱいそんでじぇそんをぱーすする", ["Python", "JSON"]),
        ("りあくとのゆーずえふぇくとふっくをつかう", ["React", "useEffect"]),
        ("どっかーこんてなをきどうする", ["Docker"]),
        ("じっと こみっと でへんこうをほぞんする", ["git", "commit"]),
    ]

    print(f"\n🧪 テスト実行:")
    print("-" * 60)

    passed = 0
    failed = 0

    for i, (input_text, expected_keywords) in enumerate(test_cases, 1):
        print(f"\n[テスト {i}/{len(test_cases)}]")
        print(f"入力: {input_text}")

        try:
            output = correct_with_gemini(input_text)
            print(f"出力: {output}")

            # キーワードチェック
            missing = [kw for kw in expected_keywords if kw not in output]

            if not missing:
                print(f"✅ PASS: すべてのキーワード ({', '.join(expected_keywords)}) を含む")
                passed += 1
            else:
                print(f"❌ FAIL: 以下のキーワードが含まれていません: {', '.join(missing)}")
                failed += 1

        except Exception as e:
            print(f"❌ FAIL: エラーが発生しました: {e}")
            failed += 1

    # 結果サマリー
    print("\n" + "=" * 60)
    print(f"テスト結果: {passed} PASS / {failed} FAIL")
    print("=" * 60)


if __name__ == "__main__":
    test_gemini()
