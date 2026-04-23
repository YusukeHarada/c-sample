# GitHub ブランチ保護ルール設定ガイド

このドキュメントは、git-flow ワークフロー実装のための GitHub ブランチ保護ルール設定手順です。

## 前提条件

- リポジトリの管理者権限が必要
- `main` および `develop` ブランチが存在すること

## 設定手順

### 1. リポジトリ設定画面へアクセス

1. GitHub でリポジトリを開く
2. **Settings** タブをクリック
3. **Branches** メニューをクリック（左サイドバー）

### 2. main ブランチの保護ルール設定

#### Rules for `main` ブランチ

**Settings > Branches > Branch protection rules > Add rule**

以下の値を設定：

|設定項目|値|
|--------|---|
| Branch name pattern | `main` |

#### 保護内容

**Merge settings**
- ✅ **Require a pull request before merging**
  - ✅ **Require approvals**: `1`
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**
  - ✅ **Require review from Code Owners**: （オプション）

- ✅ **Require status checks to pass before merging**
  - ✅ **Require branches to be up to date before merging**
  - 必要なステータスチェック：
    - `build` (GitHub Actions workflow)
    - `test` (GitHub Actions workflow)
    - `analysis` (GitHub Actions workflow)

- ✅ **Require code reviews before merging**

- ✅ **Require conversation resolution before merging**

**Advanced options**
- ✅ **Require signed commits**（推奨）
- ✅ **Restrict who can push to matching branches**（オプション）

#### 適用対象
- ✅ **Include administrators** - 管理者もルールに従う

---

### 3. develop ブランチの保護ルール設定

#### Rules for `develop` ブランチ

**Settings > Branches > Branch protection rules > Add rule**

以下の値を設定：

|設定項目|値|
|--------|---|
| Branch name pattern | `develop` |

#### 保護内容

**Merge settings**
- ✅ **Require a pull request before merging**
  - ✅ **Require approvals**: `1`
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**

- ✅ **Require status checks to pass before merging**
  - ✅ **Require branches to be up to date before merging**
  - 必要なステータスチェック：
    - `build`
    - `test`

- ✅ **Require conversation resolution before merging**

**Advanced options**
- ❌ **Require signed commits**（主流ではないため）

#### 適用対象
- ✅ **Include administrators**

---

### 4. feature、release、hotfix ブランチの保護（オプション）

追加で設定したい場合：

#### Rules for `release/*` ブランチ

```
Branch name pattern: release/*
- Require a pull request before merging
- Require approvals: 1
- Require status checks to pass before merging
```

#### Rules for `hotfix/*` ブランチ

```
Branch name pattern: hotfix/*
- Require a pull request before merging
- Require approvals: 1
- Require status checks to pass before merging
```

---

## GitHub Actions ワークフロー設定

ブランチ保護ルールで指定するステータスチェック（`build`, `test`, `analysis`）は、
GitHub Actions ワークフローで定義されている必要があります。

### 確認方法

```
Settings > Actions > General > Workflow permissions
```

### 必要なワークフロー

プロジェクトの `.github/workflows/` ディレクトリに以下のワークフローが存在することを確認：

- ✅ **テストワークフロー** (`test.yml` など)
- ✅ **ビルドワークフロー** (`build.yml` など)
- ✅ **静的解析ワークフロー** (`analysis.yml` など)

---

## トラブルシューティング

### Q: ステータスチェック（`build` など）が見つからない

**A:** 
1. GitHub Actions ワークフローが実行されていることを確認
2. ワークフロー YAML ファイルの `jobs:` で、job-id が正しく設定されているか確認
3. `.github/workflows/` にワークフローファイルが存在するか確認

### Q: PR がいつもまでもマージできない

**A:**
1. すべてのステータスチェックが ✅ になっているか確認
2. コードレビューが完了しているか確認
3. ブランチが最新の状態に更新されているか確認（Resolve conflicts）

### Q: 管理者が直接 push してしまった

**A:**
1. ブランチ保護ルールで `Include administrators` が有効か確認
2. 管理者権限を制限する場合は、`Restrict who can push to matching branches` を設定

### Q: ホットフィックスを緊急にマージしたい

**A:**
1. 一時的にブランチ保護ルールを無効化（推奨しない）
2. または、ルール設定で `Restrict who can push to matching branches` で特定ユーザーのみ許可
3. 本来は、ワークフロー実行を早める（`workflow_run` トリガー等を使用）

### Q: Require signed commits でいつも失敗する

**A:**
1. git コミット署名が設定されているか確認
   ```bash
   git config --global user.signingkey <KEY_ID>
   git config --global commit.gpgsign true
   ```
2. または、ブランチ保護ルールで署名要件を無効化

---

## 参考資料

### GitHub 公式ドキュメント

- [About branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Managing a branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [Requiring status checks before merging](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/requiring-status-checks-before-merging)
- [Requiring code reviews before merging](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/requiring-a-pull-request-review-before-merging)

### git-flow リファレンス

- [Refer to GIT_FLOW.md](GIT_FLOW.md)

---

## よくある設定パターン

### 小規模なチーム（1-3人）

```
main:
  - Require 1 approval
  - Require status checks
  
develop:
  - Require 1 approval
  - Require status checks
```

### 中規模なチーム（4-10人）

```
main:
  - Require 2 approvals
  - Require status checks
  - Require all conversations resolved
  
develop:
  - Require 1 approval
  - Require status checks
```

### 大規模なチーム（10人以上）

```
main:
  - Require 2 approvals (including CODEOWNERS)
  - Require all status checks
  - Require all conversations resolved
  - Require signed commits
  - Dismiss stale PR approvals
  
develop:
  - Require 1 approval
  - Require status checks
  - Restrict push access (only maintainers)
```

---

## 設定完了確認

✅ すべての設定が完了したら、以下で確認：

```bash
# ローカルで develop にチェックアウト
git checkout develop

# feature ブランチを作成してテスト
git checkout -b feature/test-protection

# コミット
git commit --allow-empty -m "test: test branch protection"
git push origin feature/test-protection

# GitHub で PR を作成してテスト
# - ステータスチェックが実行される
# - レビューが求められる
# - すべてが成功したらマージ可能になる

# テストブランチを削除
git branch -D feature/test-protection
git push origin --delete feature/test-protection
```

---

ご不明な点は、リポジトリ Issue で報告してください。
