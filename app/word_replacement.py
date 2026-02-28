"""
ワードリプレイスメント（音声認識後のテキスト変換）
"""
import csv
import threading
from pathlib import Path
from typing import List, Tuple

CSV_PATH = Path(__file__).parent.parent / "__generated__" / "word_replacement.csv"


class WordReplacementManager:
    """音声認識結果に対してワード変換ルールを適用するマネージャー"""

    def __init__(self) -> None:
        self._rules: List[Tuple[str, str]] = []
        self._lock = threading.Lock()
        if CSV_PATH.exists():
            self._load_csv()
        else:
            self.save_csv()

    def _load_csv(self) -> None:
        """CSVファイルからルールを読み込む（input,output 形式）"""
        rules: List[Tuple[str, str]] = []
        try:
            with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    input_word = row.get("input", "").strip()
                    output_word = row.get("output", "").strip()
                    if input_word and output_word is not None:
                        rules.append((input_word, output_word))
        except Exception:
            pass
        with self._lock:
            self._rules = rules

    def apply(self, text: str) -> str:
        """ルール一覧を順番に適用してテキストを変換する"""
        with self._lock:
            rules = list(self._rules)
        for input_word, output_word in rules:
            text = text.replace(input_word, output_word)
        return text

    def get_rules(self) -> List[Tuple[str, str]]:
        """ルール一覧を取得する"""
        with self._lock:
            return list(self._rules)

    def set_rules(self, rules: List[Tuple[str, str]]) -> None:
        """ルールをメモリに設定する"""
        with self._lock:
            self._rules = [(inp, out) for inp, out in rules if inp]

    def save_csv(self) -> None:
        """config/word_replacement.csv にルールを保存する"""
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            rules = list(self._rules)
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["input", "output"])
            for input_word, output_word in rules:
                writer.writerow([input_word, output_word])


word_replacer = WordReplacementManager()
