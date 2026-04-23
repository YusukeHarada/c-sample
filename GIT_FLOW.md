# git-flow ブランチ戦略ガイド

このプロジェクトは **git-flow** ブランチモデルを採用しています。

## ブランチ構成

### メインブランチ（常時存在）

#### `main` ブランチ
- **用途**: 本番環境での公開リリースのみ
- **基準**: 安定した、リリース可能なコードのみ
- **命名**: なし（唯一のメインブランチ）
- **保護**: ✅ Pull Request が必須、直接pushは禁止

#### `develop` ブランチ
- **用途**: 次のリリース向けの開発統合ブランチ
- **基準**: テスト済みで統合されたコード
- **命名**: なし（唯一の開発ブランチ）
- **保護**: ✅ Pull Request が必須、直接pushは禁止

---

### 補助ブランチ（一時的、削除される）

#### `feature/*` ブランチ（機能開発）
- **分岐元**: `develop`
- **マージ先**: `develop`
- **命名規則**: 
  ```
  feature/add-user-authentication
  feature/improve-performance
  feature/fix-typo-in-help
  ```
- **ライフスパン**: 機能完成まで
- **PR**: 必須（最低1人のコードレビュー推奨）

**作成方法:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
# 開発を進める
git push origin feature/your-feature-name
# GitHub で PR を作成 → develop へマージ
```

#### `release/*` ブランチ（リリース準備）
- **分岐元**: `develop`
- **マージ先**: `main` と `develop` の両方
- **命名規則**: 
  ```
  release/1.0.0
  release/1.1.0
  ```
- **ライフスパン**: リリースの準備・テスト期間
- **用途**: 
  - バージョン番号の更新
  - バグ修正（重大なバグのみ）
  - リリースノート作成

**作成方法:**
```bash
git checkout develop
git pull origin develop
git checkout -b release/1.0.0
# バージョン更新、リリースノート作成など
git push origin release/1.0.0
# PR を作成 → main へマージ
# 同時に develop へもマージ
```

#### `hotfix/*` ブランチ（本番バグ修正）
- **分岐元**: `main`
- **マージ先**: `main` と `develop` の両方
- **命名規則**: 
  ```
  hotfix/1.0.1
  hotfix/security-patch
  ```
- **ライフスパン**: バグ修正とテスト期間のみ
- **用途**: 本番環境の緊急バグ修正

**作成方法:**
```bash
git checkout main
git pull origin main
git checkout -b hotfix/1.0.1
# バグを修正
git push origin hotfix/1.0.1
# PR を作成 → main へマージ
# 同時に develop へもマージ
```

---

## ワークフロー例

### 1. 新機能開発

```bash
# Step 1: 最新の develop を取得
git fetch origin
git checkout develop
git pull origin develop

# Step 2: feature ブランチを作成
git checkout -b feature/add-new-function

# Step 3: 開発・コミット
# ... コード編集 ...
git add .
git commit -m "feat: add new function description"

# Step 4: プッシュと PR 作成
git push origin feature/add-new-function
# GitHub で PR を作成 (base: develop, compare: feature/add-new-function)

# Step 5: コードレビュー完了後、マージ
# GitHub のマージボタンで develop へマージ

# Step 6: ローカル整理
git checkout develop
git pull origin develop
git branch -d feature/add-new-function
```

### 2. リリース準備（本番デプロイ）

```bash
# Step 1: release ブランチ作成
git checkout -b release/1.0.0 develop
git push origin release/1.0.0

# Step 2: バージョン更新・テスト
# version を 1.0.0 に更新
# README や CHANGELOG を更新
git add -A
git commit -m "chore: bump version to 1.0.0"
git push origin release/1.0.0

# Step 3: PR で main へマージ
# GitHub で PR 作成 (base: main, compare: release/1.0.0)
# レビュー後、マージ＋タグ付け
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Step 4: develop にも同じ変更をマージ
git checkout develop
git pull origin develop
git merge --no-ff release/1.0.0
git push origin develop

# Step 5: release ブランチ削除
git branch -d release/1.0.0
git push origin --delete release/1.0.0
```

### 3. 本番バグ修正（緊急時）

```bash
# Step 1: main から hotfix ブランチ作成
git checkout main
git pull origin main
git checkout -b hotfix/1.0.1

# Step 2: バグ修正
# ... コード修正 ...
git add -A
git commit -m "fix: critical bug in function X"
git push origin hotfix/1.0.1

# Step 3: main へマージ
# PR 作成 (base: main, compare: hotfix/1.0.1)
# レビュー後、マージ＋タグ付け
git checkout main
git pull origin main
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1 -m "Hotfix version 1.0.1"
git push origin v1.0.1

# Step 4: develop へもマージ
git checkout develop
git pull origin develop
git merge --no-ff hotfix/1.0.1
git push origin develop

# Step 5: hotfix ブランチ削除
git branch -d hotfix/1.0.1
git push origin --delete hotfix/1.0.1
```

---

## コミットメッセージ規則

[Conventional Commits](https://www.conventionalcommits.org/) に従います：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### type の種類
- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメント更新
- **style**: コード形式（スペース、セミコロン等。ロジック変更なし）
- **refactor**: リファクタリング
- **perf**: パフォーマンス改善
- **test**: テスト追加・修正
- **chore**: ビルド、依存関係、その他（本体ロジック変更なし）
- **ci**: CI/CD 設定変更

### 例

```bash
git commit -m "feat(add): add new arithmetic function"
git commit -m "fix(main): correct overflow handling in multiply"
git commit -m "docs: update README with setup instructions"
git commit -m "test(add): add test cases for negative numbers"
git commit -m "chore: bump version to 1.0.0"
```

---

## CI/CD での自動テスト

各ブランチへのプッシュ・PR 作成時に GitHub Actions が自動実行されます：

| ブランチ | テスト | 構築 | レポート | デプロイ |
|---------|--------|------|---------|---------|
| `feature/*` | ✅ | ✅ | ✅ | ❌ |
| `develop` | ✅ | ✅ | ✅ | ❌ |
| `release/*` | ✅ | ✅ | ✅ | ❌ |
| `main` | ✅ | ✅ | ✅ | ✅ (タグ) |
| `hotfix/*` | ✅ | ✅ | ✅ | ✅ (タグ) |

---

## GitHub ブランチ保護ルール設定

リポジトリ管理者が以下を設定してください：

### `main` ブランチ保護

**Settings → Branches → Branch protection rules**

```
Branch name pattern: main
□ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Require conversation resolution before merging
☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
☑ Require code reviews before merging
☑ Dismiss stale pull request approvals when new commits are pushed
☑ Require the most recent push to have been approved
☑ Require signed commits
```

### `develop` ブランチ保護

**Settings → Branches → Branch protection rules**

```
Branch name pattern: develop
□ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Require conversation resolution before merging
☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
```

---

## トラブルシューティング

### ブランチ名を間違えた場合

```bash
# ローカルで名前変更
git branch -m old_name new_name

# リモートを削除して再プッシュ
git push origin :old_name
git push origin new_name
```

### マージコンフリクトの解決

```bash
# コンフリクト発生時、ファイルを編集
git add <resolved-file>
git commit -m "Merge: resolve conflicts"
git push
```

### タグの管理

```bash
# タグ一覧表示
git tag -l

# タグ削除（ローカル）
git tag -d v1.0.0

# タグ削除（リモート）
git push origin --delete v1.0.0
```

---

## 参考資料

- [git-flow cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)
- [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
