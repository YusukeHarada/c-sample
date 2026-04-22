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

---

更に私の方で `make` / `make test` を実行して動作確認を希望される場合は、実行して確認します（環境に依存する外部パッケージが必要になることがあります）。