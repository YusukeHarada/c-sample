# c-sample

C言語で書かれた簡単なサンプルプロジェクトです。Google Test を使った単体テスト、静的解析、カバレッジ測定のための `Makefile` を同梱しています。

## 主要ファイル構成
- `main.c`, `main.h` - 実装とヘッダ
- `test_main.cc` - Google Test によるテスト
- `test/test_main.c` - Unity（Ceedling）による同じ関数のテスト
- `project.yml` - Ceedling の設定
- `ci/` - CI 用のスクリプトと設定（警告ベースライン、メモリ上限、MISRA アドオン設定）
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

`main` への push・pull request・毎日の定期実行（0:00 JST）・手動実行で動きます。ビルドだけでなく、品質の指標を自動で取って PR 上に見せることを目的にしています。

### ジョブ構成

```
build ──┬─ warning_gate   コンパイラ警告がベースラインより増えたら失敗
        └─ memory_usage   ROM/RAM 使用率が上限を超えたら失敗
cppcheck                  MISRA 以外の指摘は失敗、MISRA は PR 上に注釈で表示
complexity                関数の複雑度がしきい値を超えたら注釈で表示（失敗させない）
unit_test_gtest           Google Test + カバレッジ（gcovr）
unit_test_ceedling        Unity/CMock（Ceedling）+ カバレッジ
metrics_summary           main への push・定期実行時に、指標の推移 CSV を更新
```

| ジョブ | 使うツール | 判定 |
|:--|:--|:--|
| build | gcc, make | 警告を多めに出すフラグ（`STRICT_CFLAGS`）でビルド |
| warning_gate | `ci/scripts/count_warnings.py` | 警告数 > `ci/warning_baseline.txt` で失敗 |
| memory_usage | `ci/scripts/memory_usage.py`（pyelftools） | `ci/memory_limits.json` の上限超過で失敗 |
| cppcheck | Cppcheck + MISRA アドオン、`ci/scripts/annotate.py` | MISRA 以外の指摘で失敗 |
| complexity | lizard、`ci/scripts/annotate.py` | 失敗させない（見える化のみ） |
| unit_test_gtest | Google Test, gcovr | テスト失敗で失敗 |
| unit_test_ceedling | Ceedling 1.0（Unity, CMock）, gcovr | テスト失敗で失敗 |
| metrics_summary | `ci/scripts/summarize.py`, gh | 推移 CSV（`metrics-history`）を 90 日保持 |

### 結果の確認

- 各ジョブの Summary に、警告数・ROM/RAM 使用率・静的解析の指摘一覧・テスト結果・カバレッジが表示されます。
- PR の「Files changed」では、Cppcheck・lizard の指摘が該当行に注釈として表示されます（GitHub の仕様で、1 ステップあたり種類ごとに最大 10 件）。
- カバレッジの HTML レポートは Artifacts の `test-report-gtest` / `test-report-ceedling` からダウンロードできます。
- 指標の推移は Artifacts の `metrics-history`（CSV）で確認できます。

### 運用のしかた

- 警告を減らしたら `ci/warning_baseline.txt` の値を下げてコミットします（ベースラインは手元で `python3 ci/scripts/count_warnings.py build.log --baseline ci/warning_baseline.txt --update` でも更新できます）。
- `ci/memory_limits.json` はホスト PC 向けの仮想ターゲット（ROM 16KB / RAM 2KB）です。実機では `regions` にメモリ領域のアドレスとサイズを定義します。
- MISRA の指摘はルール番号のみ表示されます。ルール本文は MISRA 規格書（有償）を参照してください。Cppcheck の MISRA アドオンは一部ルールのみの対応で、準拠の証跡にはなりません。

### ローカルでの実行

```bash
# 単体テスト（Unity / Ceedling 版）
gem install ceedling -v 1.0.0
LANG=C.UTF-8 ceedling gcov:all        # 結果: build/artifacts/gcov/

# 解析スクリプト（Python 3.10 以上）
pip install lizard pyelftools
make CFLAGS="-Wall -Wextra -Wpedantic -Wstrict-prototypes -Wmissing-prototypes -Wconversion" 2>&1 | tee build.log
python3 ci/scripts/count_warnings.py build.log --baseline ci/warning_baseline.txt
python3 ci/scripts/memory_usage.py main --config ci/memory_limits.json
```

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

https://YusukeHarada.github.io/c-sample/

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
