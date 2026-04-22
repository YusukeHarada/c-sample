# c-sample

C言語で書かれた簡単なプログラムのサンプルです。Google testを使用した単体テストが含まれています。

## ビルド方法

### メインプログラムのビルド
```bash
make
```

実行ファイル `main` が生成されます。

## 実行方法

### メインプログラムの実行
```bash
./main
```

## テスト方法（Google test）

### 前提条件
Google testをシステムにインストール:
```bash
sudo apt-get update
sudo apt-get install -y libgtest-dev
```

### テストの実行
```bash
make test
```

テストをビルドして自動的に実行します。

テスト結果例：
```
[==========] Running 6 tests from 2 test suites.
[----------] Global test environment set-up.
[----------] 2 tests from AddTest
[ RUN      ] AddTest.PositiveNumbers
[       OK ] AddTest.PositiveNumbers (0 ms)
[ RUN      ] AddTest.NegativeNumbers
[       OK ] AddTest.NegativeNumbers (0 ms)
[ RUN      ] AddTest.MixedNumbers
[       OK ] AddTest.MixedNumbers (0 ms)
[----------] 3 tests from MultiplyTest
[ RUN      ] MultiplyTest.PositiveNumbers
[       OK ] MultiplyTest.PositiveNumbers (0 ms)
[ RUN      ] MultiplyTest.Zero
[       OK ] MultiplyTest.Zero (0 ms)
[ RUN      ] MultiplyTest.NegativeNumbers
[       OK ] MultiplyTest.NegativeNumbers (0 ms)
[==========] 6 tests from 2 test suites ran.
```

## クリーンアップ

```bash
make clean
```

ビルド成果物（outフォルダとmainを削除）

## テストケース一覧

### AddTest (カバレッジ: 100%)
- `PositiveNumbers` - 正の数の加算テスト（2 + 3 = 5）
- `NegativeNumbers` - 負の数の加算テスト（-2 + -3 = -5）
- `MixedNumbers` - 正と負の混合加算テスト（5 + -3 = 2）
- `Zero` - ゼロの加算テスト（0 + 0 = 0）

### MultiplyTest (カバレッジ: 100%)
- `PositiveNumbers` - 正の数の乗算テスト（2 × 3 = 6）
- `Zero` - ゼロを含む乗算テスト（5 × 0 = 0）
- `NegativeNumbers` - 負の数の乗算テスト（-2 × 3 = -6）
- `One` - 1を含む乗算テスト（5 × 1 = 5）

### ProgramTest (カバレッジ: 100%)
- `RunProgram` - プログラムメイン処理のテスト
  - run_program() 関数の実行確認
  - 標準出力への正常な出力動作検証

**テスト統計:**
- 総テストケース数: 11
- カバレッジ: C0 100%（全行実行）

## 静的コード解析

### ローカル環境での実行
```bash
make check
```

以下の解析を実行します：
- **cppcheck** - Cコードの静的解析
- **コンパイラ警告チェック** - 厳密なオプション（-Wall -Wextra -Werror）でのビルド

### 前提条件
cppchecのインストール:
```bash
sudo apt-get install -y cppcheck
```

## CI/CD（自動テスト）

### GitHub Actions による自動化

このプロジェクトはGitHub Actionsで以下が自動実行されます：

**トリガー条件:**
- `main` ブランチへのpush時
- `main` ブランチへのpull request時

**実行される処理:**

| ステップ | 説明 |
|--------|------|
| ビルド | `make` でメインプログラムをビルド |
| 単体テスト | `make test` でGoogle testを実行 |
| 静的解析 | `cppcheck` でコード品質をチェック |
| 警告チェック | 厳密なコンパイラ警告でのビルド確認 |

### ワークフローファイル
`.github/workflows/ci.yml` でCI設定を管理しています。

### 実行状態の確認
リポジトリのGitHub Actionsタブで、ワークフロー実行結果を確認できます。

## カバレッジ測定（C0/C1カバレッジ）

### 概要
- **C0カバレッジ（ステートメントカバレッジ）** - 実行されたコード行の割合
- **C1カバレッジ（分岐カバレッジ）** - 実行されたコード分岐の割合

### ローカル環境での実行

#### 前提条件
```bash
sudo apt-get install -y gcovr lcov
```

#### C0カバレッジレポート生成
```bash
make coverage
```

テストを実行しながらカバレッジデータを収集し、コンソールに行数ベースのカバレッジを表示します。

出力例：
```
C0 (Line) Coverage Report:
================================
Lines executed:100.00% of 8
```

#### HTML形式のカバレッジレポート生成
```bash
make coverage-html
```

HTMLレポートが `out/coverage/html/index.html` に生成されます。
ブラウザで開いて、詳細なカバレッジ情報を確認できます。

### カバレッジレポートの見方

| メトリクス | 説明 |
|----------|------|
| Line Coverage (C0) | ソースコード行がテストで実行された割合 |
| Branch Coverage (C1) | if文などの分岐がテストで実行された割合 |
| Function Coverage | 関数がテストで呼び出された割合 |

### CI/CDでのカバレッジ測定

GitHub Actionsで自動的にカバレッジ測定が実行され、結果は**Artifacts**として保存されます。

ワークフロー実行後、以下の手順で確認できます：
1. GitHub Actionsタブを開く
2. ワークフロー実行結果をクリック
3. 下部の「Artifacts」から「coverage-report」をダウンロード
4. ローカルで `coverage/html/index.html` を開く

### カバレッジ測定コマンド一覧

| コマンド | 説明 |
|--------|------|
| `make coverage` | C0カバレッジレポートをコンソールに表示 |
| `make coverage-html` | HTMLカバレッジレポートを生成 |
| `make clean` | カバレッジデータを含むすべての成果物を削除 |