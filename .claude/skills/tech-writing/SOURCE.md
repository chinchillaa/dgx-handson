# 出典

このスキルは [malanjp/skills](https://github.com/malanjp/skills) の `tired-dev` プラグインに含まれる `tech-writing` を、本プロジェクトで再利用するために複製したものです。

| 項目 | 値 |
|---|---|
| 取得元 | https://github.com/malanjp/skills.git |
| コミット | `54713f30e24d630a9d404668281530b3a326f384`（2026-10-08） |
| ライセンス | MIT（`LICENSE` を参照） |

## 複製したファイル

| このディレクトリ | 取得元のパス |
|---|---|
| `SKILL.md` | `plugins/tired-dev/SKILL.md`（規約の全文） |
| `references/anchor.md` | `plugins/tired-dev/rules/anchor.md`（規約の要約） |
| `references/template-examples.md` | `plugins/tired-dev/eval/template-examples.md`（記入例） |

## 更新手順

リポジトリのルートで次を実行し、取得元の最新版で上書きします。
上書き後はこのファイルのコミット欄を更新してください。

```bash
tmp=$(mktemp -d) && git clone --depth 1 https://github.com/malanjp/skills.git "$tmp" \
  && cp "$tmp/plugins/tired-dev/SKILL.md" .claude/skills/tech-writing/SKILL.md \
  && cp "$tmp/plugins/tired-dev/rules/anchor.md" .claude/skills/tech-writing/references/anchor.md \
  && cp "$tmp/plugins/tired-dev/eval/template-examples.md" .claude/skills/tech-writing/references/template-examples.md \
  && git -C "$tmp" log -1 --format='%H %cs'
```
