# Contributing to c-sample

c-sample へのご貢献ありがとうございます！このドキュメントは、プロジェクトへ参加するための方法をガイドします。

## 行動規範

このプロジェクトの参加者は、すべての相互作用で尊重、包括性、専門性を保つことを期待しています。

## 貢献方法

### 1. Issue の報告

バグを発見した場合や改善提案がある場合は、GitHub Issues で報告してください。

**バグレポートの場合:**
```
タイトル: [BUG] 簡潔な問題説明

説明:
- 何が起こったか
- 期待される動作
- 再現手順

環境:
- OS: 
- gcc バージョン: 
```

**機能リクエストの場合:**
```
タイトル: [FEATURE] 新機能の説明

説明:
- なぜこの機能が必要か
- どのように実装するか
- 使用例
```

### 2. コード貢献プロセス

#### Step 1: リポジトリの fork / clone

```bash
# fork の場合
git clone https://github.com/YOUR_USERNAME/c-sample.git
cd c-sample
git remote add upstream https://github.com/YusukeHarada/c-sample.git

# または、直接 clone（push権限がある場合）
git clone https://github.com/YusukeHarada/c-sample.git
cd c-sample
```

#### Step 2: git-flow に従う

詳細は [GIT_FLOW.md](GIT_FLOW.md) を参照してください。

```bash
# 最新の develop ブランチを取得
git fetch origin
git checkout develop
git pull origin develop

# feature ブランチを作成
git checkout -b feature/your-feature-name

# 開発を進める
# ... コード編集 ...

# コミット（Conventional Commits に従う）
git add .
git commit -m "feat: add your feature description"

# リモートにプッシュ
git push origin feature/your-feature-name
```

#### Step 3: Pull Request 作成

GitHub で PR を作成してください。PR テンプレート（存在する場合）に従い、以下を記入してください：

```markdown
## 変更内容
ここで何を変更したかを説明してください

## 関連する Issue
Closes #123

## 変更の背景
この変更が必要な理由を説明してください

## テスト方法
テストしたことを記入してください
- [ ] `make test` で全テスト成功
- [ ] `make coverage` でカバレッジ確認
- [ ] `make check` で静的解析合格

## スクリーンショット（該当する場合）
必要に応じて追加

## チェックリスト
- [ ] コミットメッセージが Conventional Commits に従っている
- [ ] テストが追加/更新されている
- [ ] ドキュメントが更新されている
- [ ] Doxygen コメントが追加されている
- [ ] 警告が出ていない (`make check` 合格)
```

#### Step 4: コードレビュー

メンテナーがコードレビューを行います。以下の点を確認します：

- **コード品質**: 読みやすさ、保守性
- **テスト**: 十分なテストカバレッジ
- **ドキュメント**: 説明が明確か
- **スタイル**: プロジェクトの規則に従っているか
- **CI/CD**: GitHub Actions のすべてのテストが成功しているか

フィードバックがある場合は、修正して新しいコミットをプッシュしてください。

#### Step 5: マージ

レビューが完了し、承認されたら、PR がマージされます。

### 3. コーディングスタイル

#### C言語スタイル

```c
/**
 * @brief 関数の説明
 * @param param1 パラメータ説明
 * @return 戻り値説明
 */
int function_name(int param1, int param2)
{
    /* 関数の処理 */
    int result = param1 + param2;
    
    return result;
}
```

#### ガイドライン

- **インデント**: スペース 4 個
- **行の長さ**: 最大 100 文字（推奨）
- **命名規則**:
  - 関数: `snake_case` (例: `calculate_sum`)
  - 定数: `UPPER_SNAKE_CASE` (例: `MAX_SIZE`)
  - ローカル変数: `snake_case` (例: `result`)
- **ブレース**: Allman スタイル（開き括弧は改行）

```c
if (condition)
{
    // 処理
}
else
{
    // 処理
}
```

#### コメント

- 複雑なロジックには詳細なコメントを入れる
- Doxygen フォーマットで公開API にはコメントを入れる
- 明らかなコードにはコメント不要

### 4. テストの追加

新機能時にはテストを追加してください。

```cpp
// test_main.cc
TEST(MyNewFeatureTest, PositiveCase)
{
    EXPECT_EQ(my_function(5, 3), 8);
}

TEST(MyNewFeatureTest, EdgeCase)
{
    EXPECT_EQ(my_function(0, 0), 0);
}
```

テスト実行:

```bash
# テスト実行
make test

# カバレッジ確認
make coverage

# HTML レポート
make coverage-html
```

### 5. ドキュメント更新

- API に変更がある場合は、Doxygen コメントを更新
- 新しい機能は README.md に追加
- 重要な手順は GIT_FLOW.md を参照

```bash
# ドキュメント生成
make docs
```

### 6. コミット前チェック

```bash
# コンパイル確認
make clean
make

# テスト実行
make test

# 静的解析
make check

# カバレッジ確認
make coverage
```

## ブランチ保護ルール

以下のルールが適用されます：

| ブランチ | PR必須 | レビュー | テスト | 署名 |
|---------|--------|---------|--------|------|
| `main` | ✅ | ✅ | ✅ | 推奨 |
| `develop` | ✅ | ✅ | ✅ | 推奨 |

## リリースプロセス

メンテナーのみが実施します。メンテナー向けドキュメントは [GIT_FLOW.md](GIT_FLOW.md) の「リリース準備」セクションを参照してください。

## よくある質問

### Q: どのブランチから作業すればよい？

**A:** 新機能の場合は `develop`、本番バグの場合は `main` から分岐してください。詳細は [GIT_FLOW.md](GIT_FLOW.md) を参照。

### Q: コミットメッセージのフォーマットは？

**A:** [Conventional Commits](https://www.conventionalcommits.org/) に従ってください。例: `feat: add new function`

### Q: テストなしで PR できる？

**A:** テストは必須です。`make test` で全テスト成功が条件です。

### Q: ドキュメントは英語？日本語？

**A:** ドキュメント（README.md等）は日本語、コード内コメント（英語も可）は対応付けが混在していますが、統一方針に従ってください。

## サポート

質問や問題がある場合：

1. **Issue 質問**: GitHub Issues で質問
2. **実装相談**: PR でのコメント欄で相談
3. **プルリクエスト**: わからないことはコメントしてください

## ライセンス

このプロジェクトへの貢献により、あなたの著作物はプロジェクトのライセンスの下で公開されることに同意します。

---

協力をお待ちしています！🚀
