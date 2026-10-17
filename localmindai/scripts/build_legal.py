#!/usr/bin/env python3
"""LocalMindAI のアプリ内法務ドキュメント（Markdown）から公開ページを生成する。

使い方: python3 scripts/build_legal.py [LocalMind の Resources/Legal のパス]

入力: {privacy,terms}-{lang}.md（アプリ内で表示しているものと同じファイル）
出力: localmindai/{privacy,terms}.html（言語ごとの <section> を持つ 1 ファイル）

アプリ内の表示と文面を同じに保つため、HTML は手で書かずここから生成する。
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

# アプリ側の Markdown の場所。第 1 引数で上書きできる。
DEFAULT_LEGAL_DIR = Path.home() / "Documents/project/AI_LLM/Apps/LocalMind/LocalMind/Resources/Legal"
# 出力先はこのスクリプトの親（localmindai/）
OUT_DIR = Path(__file__).resolve().parent.parent

# アプリ本体の CFBundleLocalizations と同じ順・同じ言語
LANGS = ["ja", "en", "zh-Hans", "zh-Hant", "ko", "es", "fr", "de", "pt-BR", "it"]

# LegalInfo（LegalDocumentView.swift）と同じ値
OPERATOR = "utsugumi"
CONTACT_EMAIL = "utsugumi@icloud.com"
EFFECTIVE_DATE = "2026-10-13"
MINIMUM_AGE = "13"

# 各言語の「アプリのトップへ戻る」リンク文言とツールバーのラベル
BACK = {
    "ja": "← LocalMindAI トップへ",
    "en": "← LocalMindAI home",
    "zh-Hans": "← 返回 LocalMindAI 首页",
    "zh-Hant": "← 返回 LocalMindAI 首頁",
    "ko": "← LocalMindAI 홈으로",
    "es": "← Inicio de LocalMindAI",
    "fr": "← Accueil LocalMindAI",
    "de": "← LocalMindAI Startseite",
    "pt-BR": "← Início do LocalMindAI",
    "it": "← Home di LocalMindAI",
}
LANG_LABEL = {
    "ja": "言語", "en": "Language", "zh-Hans": "语言", "zh-Hant": "語言", "ko": "언어",
    "es": "Idioma", "fr": "Langue", "de": "Sprache", "pt-BR": "Idioma", "it": "Lingua",
}
# もう一方の法務ページへのリンク文言（アプリの settings.legal.* と同じ訳語）
DOC_TITLE = {
    "privacy": {
        "ja": "プライバシーポリシー", "en": "Privacy Policy", "zh-Hans": "隐私政策",
        "zh-Hant": "隱私權政策", "ko": "개인정보 처리방침", "es": "Política de privacidad",
        "fr": "Politique de confidentialité", "de": "Datenschutzerklärung",
        "pt-BR": "Política de Privacidade", "it": "Informativa sulla privacy",
    },
    "terms": {
        "ja": "利用規約", "en": "Terms of Use", "zh-Hans": "使用条款", "zh-Hant": "使用條款",
        "ko": "이용약관", "es": "Términos de uso", "fr": "Conditions d’utilisation",
        "de": "Nutzungsbedingungen", "pt-BR": "Termos de Uso", "it": "Termini di utilizzo",
    },
}
SUPPORT_TITLE = {
    "ja": "サポート", "en": "Support", "zh-Hans": "支持", "zh-Hant": "支援", "ko": "지원",
    "es": "Soporte", "fr": "Assistance", "de": "Support", "pt-BR": "Suporte", "it": "Assistenza",
}

URL_RE = re.compile(r"(https?://[^\s<>()]+)")
EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def substitute(raw: str) -> str:
    """アプリ側と同じプレースホルダ置換（LegalDocument.text と同じ値）。"""
    return (raw
            .replace("{{OPERATOR}}", OPERATOR)
            .replace("{{CONTACT}}", f"Email: {CONTACT_EMAIL}")
            .replace("{{EFFECTIVE_DATE}}", EFFECTIVE_DATE)
            .replace("{{MINIMUM_AGE}}", MINIMUM_AGE))


def inline(text: str) -> str:
    """段落・箇条書きの中身を HTML に変換する。先にエスケープしてから装飾を足す。"""
    escaped = html.escape(text, quote=False)
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = URL_RE.sub(r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', escaped)
    escaped = EMAIL_RE.sub(r'<a href="mailto:\1">\1</a>', escaped)
    return escaped


def markdown_to_blocks(markdown: str) -> tuple[str, list[str]]:
    """見出し・箇条書き・段落だけの Markdown を (タイトル, HTML ブロック) に変換する。"""
    title = ""
    blocks: list[str] = []
    bullets: list[str] = []

    def flush() -> None:
        nonlocal bullets
        if bullets:
            items = "\n".join(f"                <li>{item}</li>" for item in bullets)
            blocks.append(f"            <ul>\n{items}\n            </ul>")
            bullets = []

    for line in markdown.splitlines():
        text = line.strip()
        if not text:
            continue
        if text.startswith("## "):
            flush()
            blocks.append(f"            <h2>{inline(text[3:])}</h2>")
        elif text.startswith("# "):
            flush()
            title = text[2:].strip()
        elif text.startswith("- "):
            bullets.append(inline(text[2:]))
        else:
            flush()
            blocks.append(f"            <p>{inline(text)}</p>")
    flush()
    return title, blocks


def section(legal_dir: Path, doc: str, lang: str) -> str:
    source = legal_dir / f"{doc}-{lang}.md"
    if not source.exists():
        raise SystemExit(f"見つかりません: {source}")
    title, blocks = markdown_to_blocks(substitute(source.read_text(encoding="utf-8")))
    if not title:
        raise SystemExit(f"タイトル（# 見出し）がありません: {source}")

    other = "terms" if doc == "privacy" else "privacy"
    page_title = f"{title} – LocalMindAI"
    body = "\n".join(blocks)
    return f"""        <section data-lang="{lang}" data-page-title="{html.escape(page_title, quote=True)}">
            <h1>{inline(title)}</h1>
{body}
            <footer>
                <p><a data-lang-href="{other}.html" href="{other}.html">{inline(DOC_TITLE[other][lang])}</a>
                    ・<a data-lang-href="support.html" href="support.html">{inline(SUPPORT_TITLE[lang])}</a></p>
                <p><a data-lang-href="./" href="./">{inline(BACK[lang])}</a></p>
            </footer>
        </section>"""


def page(legal_dir: Path, doc: str) -> str:
    sections = "\n".join(section(legal_dir, doc, lang) for lang in LANGS)
    english = DOC_TITLE[doc]["en"]
    labels = " / ".join(f"{LANG_LABEL[lang]}" for lang in ("en", "ja"))
    return f"""<!DOCTYPE html>
<!-- このファイルは scripts/build_legal.py が LocalMind の Resources/Legal/*.md から生成します。直接編集しないでください。 -->
<html class="no-js" lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{english} – LocalMindAI</title>
    <meta name="description" content="{english} for the LocalMindAI iPhone app.">
    <link rel="stylesheet" href="assets/page.css">
</head>

<body>
    <div class="toolbar">
        <label for="lang-select"><span>{labels}</span>
            <select id="lang-select" aria-label="Language"></select>
        </label>
    </div>
    <noscript>
        <p>This page can switch languages in your browser. The English text below is shown when scripts are turned off.</p>
    </noscript>

{sections}

    <script src="assets/lang.js"></script>
</body>

</html>
"""


def main(argv: list[str]) -> int:
    legal_dir = Path(argv[1]).expanduser() if len(argv) > 1 else DEFAULT_LEGAL_DIR
    if not legal_dir.is_dir():
        print(f"Legal ディレクトリがありません: {legal_dir}", file=sys.stderr)
        print("使い方: python3 scripts/build_legal.py <LocalMind の Resources/Legal のパス>", file=sys.stderr)
        return 1
    for doc in ("privacy", "terms"):
        out = OUT_DIR / f"{doc}.html"
        out.write_text(page(legal_dir, doc), encoding="utf-8")
        print(f"書き出し: {out} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
