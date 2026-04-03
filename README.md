# app-pages（GitHub Pages）

このリポジトリは [ninjya54.github.io/app-pages](https://ninjya54.github.io/app-pages/) の静的ソースです。

## 利用者向け vs 開発者向け

| 区分 | 内容 |
|------|------|
| **利用者向けに公開** | 各アプリの紹介・プライバシー・利用規約・サポートなど、一般ユーザーがブラウザで辿るページ |
| **開発者・システム専用** | `version.json` のようにアプリが **プログラムで URL を取得するだけ**のファイル、リリース手順、リポジトリ運用メモ |

**やらないこと:** 利用者向け `index.html` から `version.json` へのリンク、GitHub リポジトリへの誘導ボタン、運用メモ（`ios.latestVersion` 更新手順など）の掲載。

各アプリの README やアプリ本体リポジトリ側の `app-pages/README.md`・`.cursor/rules/app-pages-public-developer.mdc` も参照。
