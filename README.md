# c-sample

C言語で書かれた簡単なサンプルプロジェクトです。Google Test を使った単体テスト、静的解析、カバレッジ測定のための `Makefile` を同梱しています。

## 主要ファイル構成
- `main.c`, `main.h` - 実装とヘッダ
- `test_main.cc` - Google Test によるテスト
- `makefile` - ビルド / テスト / カバレッジ / 静的解析のターゲット
- `out/` - ビルド成果物（Makefile が自動作成）

## 前提（ローカル実行に必要なツール）
- `gcc`, `g++`
- `make`
- `libgtest`（システムにインストールされ、`-lgtest -lgtest_main` でリンクできること）
- `cppcheck`（静的解析）
- `gcovr`, `lcov`, `genhtml`（カバレッジ HTML レポート生成）
- `size`, `nm`（バイナリ解析表示、Makefile から参照）

Ubuntu/Debian の例:
```bash
sudo apt-get update
sudo apt-get install -y build-essential g++ gcc libgtest-dev cppcheck gcovr lcov
# libgtest-dev は環境によってはソースからビルドする必要があります。
```

## 使い方（Makefile に合わせた手順）

- メインプログラムをビルド:
```bash
make
```
生成物: 実行ファイル `main`（ワークディレクトリ直下）が生成されます。
ビルド時に `out/` ディレクトリが作成され、テスト用のオブジェクトは `out/` 内に出力されます。

- メインプログラムを実行:
```bash
./main
```

- 単体テストのビルドと実行:
```bash
make test
```
このターゲットは `out/test_main` （テスト実行ファイル）を作成し、実行します。

- 静的解析と警告チェック:
```bash
make check
```
`cppcheck` を実行し、さらにコンパイラ警告（`-Wall -Wextra -Werror`）によるチェックを行います。

- カバレッジ（C0）を取得してコンソールに要約を表示:
```bash
make coverage
```
テストをビルド／実行してカバレッジデータを収集します。

- HTML 形式のカバレッジレポート生成:
```bash
make coverage-html
```
生成先: `out/coverage/html/index.html`

- クリーン:
```bash
make clean
```
`out/` と `main`、およびカバレッジ関連ファイルを削除します。

## Makefile のポイント（要約・注意点）
- テストは `g++` でリンクされ、`-lgtest -lgtest_main -pthread` を利用します。
- `main.c` は C コンパイラ（`gcc`）でコンパイルし、テスト用オブジェクト `main_obj.o` を `out/` に配置してリンクします（Makefile の設計による）。
- カバレッジ生成時は `--coverage` フラグをコンパイルに付与します。`lcov` や `gcovr` のバージョン差異によりオプション `--ignore-errors` を使っているので、環境差での失敗に注意してください。

## トラブルシューティング（よくある問題）
- Google Test がリンクできない: `libgtest` のライブラリがシステムにインストールされていないか、ビルド済みでない可能性があります。必要に応じてシステムの gtest をビルドしてください。
- カバレッジが出ない: `.gcda`/`.gcno` が生成されているか確認し、`make clean && make coverage` を再実行してください。

## CI/CD（GitHub Actions）

このプロジェクトはGitHub Actionsで自動テストを実行します。

### トリガー条件
- `main` ブランチへのpush時
- `main` ブランチへのpull request時

### 実行される処理

| ステップ | 説明 |
|--------|------|
| ビルド | `make` でメインプログラムをビルド |
| 単体テスト | `make test` でGoogle Testを実行 |
| 静的解析 | `cppcheck` でコード品質をチェック |
| 警告チェック | 厳密なコンパイラ警告でのビルド確認 |
| カバレッジ測定 | `make coverage` でカバレッジデータを収集 |
| HTMLレポート生成 | `make coverage-html` でHTMLレポートを作成 |

### 結果の確認
GitHub Actionsタブでワークフロー実行結果を確認できます。各ステップの成功/失敗が明確に表示され、最終ステップで全体のPass/NGがまとめられます。

## ドキュメント生成（Doxygen）

このプロジェクトは **Doxygen** を使用してAPIドキュメントを自動生成し、**GitHub Pages** で公開しています。

### 前提条件（ローカル実行時）
```bash
sudo apt-get install -y doxygen graphviz
```

### ドキュメント生成方法

#### ローカルで生成
```bash
doxygen Doxyfile
```

生成されたドキュメントは `docs/html/index.html` に出力されます。

#### ブラウザで確認
```bash
# ブラウザで開く（Linux）
xdg-open docs/html/index.html

# または
firefox docs/html/index.html
```

### GitHub Pages での公開

#### 1. リポジトリ設定
GitHub リポジトリの **Settings** → **Pages** で以下を設定してください：

- **Source**: `Deploy from a branch`
- **Branch**: `gh-pages` / `/ (root)`

#### 2. 自動デプロイ
- `main` ブランチへの `push` 時に、GitHub Actions ワークフロー（`.github/workflows/doxygen.yml`）が自動的に実行されます
- ドキュメントが生成され、`gh-pages` ブランチにデプロイされます

#### 3. ドキュメントへのアクセス
生成されたドキュメントは以下のURLで公開されます：
```
https://YusukeHarada.github.io/c-sample/
```

### ドキュメント形式

ドキュメンテーションは Doxygen 形式のコメントで記述されています：

```c
/**
 * @brief 関数の簡潔な説明
 *
 * @param param1 パラメータ1の説明
 * @param param2 パラメータ2の説明
 * @return 戻り値の説明
 *
 * @example
 * @code
 * function_name(arg1, arg2); // 使用例
 * @endcode
 */
```

### トラブルシューティング

| 問題 | 原因 | 解決方法 |
|------|------|--------|
| `doxygen: command not found` | Doxygenがインストールされていない | `sudo apt-get install -y doxygen` でインストール |
| ドキュメントが生成されない | Doxyfile の設定が不正 | `Doxyfile` を確認し、`INPUT` が正しいパスに変更 |
| GitHub Pages で 404 が出る | gh-pages ブランチが存在しない | GitHub Actions ワークフローが正常に実行されるまで待機 |
| Pages 設定が見つからない | 非公開リポジトリまたは権限不足 | リポジトリを公開するか、権限を確認 |

### 参考資料
- [Doxygen 公式ドキュメント](https://www.doxygen.nl/)
- [GitHub Pages ドキュメント](https://docs.github.com/en/pages)

- **成功時**: 🎉 All CI checks passed successfully! と各項目の✅表示
- **失敗時**: ❌ Some CI checks failed! と各項目の❌表示

### カバレッジレポートの確認
ワークフロー実行後、Artifactsから「coverage-report」をダウンロードし、`coverage/html/index.html` をブラウザで開いて詳細を確認できます。

---

更に私の方で `make` / `make test` を実行して動作確認を希望される場合は、実行して確認します（環境に依存する外部パッケージが必要になることがあります）。