#!/bin/bash
# git-flow セットアップスクリプト

set -e

echo "========================================="
echo "  git-flow ブランチ戦略 セットアップ"
echo "========================================="

# 1. 現在のブランチ確認
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "✓ 現在のブランチ: $CURRENT_BRANCH"

# 2. develop ブランチの存在確認
if git rev-parse --verify develop > /dev/null 2>&1; then
    echo "✓ develop ブランチ は既に存在します"
else
    echo "📝 develop ブランチを作成します..."
    git checkout -b develop
    git push -u origin develop
    echo "✓ develop ブランチを作成してプッシュしました"
fi

# 3. main ブランチの確認
if git rev-parse --verify main > /dev/null 2>&1; then
    echo "✓ main ブランチ が存在します"
else
    echo "⚠️  main ブランチが見つかりません（デフォルトブランチ名を確認してください）"
fi

# 4. ローカルで develop に切り替え
echo "📝 develop ブランチに切り替えます..."
git checkout develop
git pull origin develop

# 5. ブランチ保護ルール設定の案内
echo ""
echo "========================================="
echo "  次のステップ: ブランチ保護ルール設定"
echo "========================================="
echo ""
echo "GitHub リポジトリの Settings → Branches で、"
echo "以下のブランチに保護ルールを設定してください："
echo ""
echo "1. main ブランチ:"
echo "   - Require a pull request before merging"
echo "   - Require approvals: 1"
echo "   - Require status checks to pass before merging"
echo ""
echo "2. develop ブランチ:"
echo "   - Require a pull request before merging"
echo "   - Require status checks to pass before merging"
echo ""
echo "詳細は GIT_FLOW.md を参照してください。"
echo ""

# 6. git-flow CLI ツールのインストール案内
echo "========================================="
echo "  オプション: git-flow CLI ツール"
echo "========================================="
echo ""
echo "git-flow を ツールコマンド で管理する場合:"
echo ""
echo "Ubuntu/Debian:"
echo "  sudo apt-get install git-flow"
echo ""
echo "macOS:"
echo "  brew install git-flow"
echo ""
echo "Windows (Git Bash):"
echo "  wget -q -O - --no-check-certificate https://github.com/nvie/gitflow/raw/develop/contrib/gitflow-installer.sh | bash"
echo ""
echo "参考: https://danielkummer.github.io/git-flow-cheatsheet/"
echo ""

# 7. 完了
echo "========================================="
echo "✅ git-flow セットアップが完了しました！"
echo "========================================="
echo ""
echo "📚 ドキュメント:"
echo "  • GIT_FLOW.md       - git-flow ワークフローガイド"
echo "  • CONTRIBUTING.md   - 貢献ガイド"
echo ""
echo "🚀 開始方法:"
echo "  1. git checkout develop"
echo "  2. git checkout -b feature/your-feature-name"
echo "  3. 開発を進める"
echo "  4. git push origin feature/your-feature-name"
echo "  5. GitHub で PR を作成"
echo ""
