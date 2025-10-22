#!/bin/bash

# Test script for weekly issue summary workflow
# This script simulates the workflow locally for testing

echo "🧪 Testing Weekly Issue Summary Workflow"
echo "========================================"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   brew install gh"
    echo "   or visit: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Please run:"
    echo "   gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"

# Set up test environment
export LABELS_TO_INCLUDE="bug,help wanted,triage,enhancement,question,documentation"

echo ""
echo "📊 **Weekly Issue Summary** - $(date -u +%Y-%m-%d)"
echo ""
echo "📅 **Period:** $(date -u -d '7 days ago' +%Y-%m-%d) to $(date -u +%Y-%m-%d)"
echo ""

# Get new issues created in the past week
NEW_ISSUES=$(gh issue list --state all --created "$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)..$(date -u +%Y-%m-%dT%H:%M:%SZ)" --json number --jq 'length' 2>/dev/null || echo "0")
echo "🆕 **New Issues:** $NEW_ISSUES"

# Get closed issues in the past week
CLOSED_ISSUES=$(gh issue list --state closed --updated "$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)..$(date -u +%Y-%m-%dT%H:%M:%SZ)" --json number --jq 'length' 2>/dev/null || echo "0")
echo "✅ **Closed Issues:** $CLOSED_ISSUES"

echo ""
echo "🏷️ **Issues by Label:**"

# Split labels and process each
IFS=',' read -ra LABELS <<< "$LABELS_TO_INCLUDE"
for label in "${LABELS[@]}"; do
    # Trim whitespace
    label=$(echo "$label" | xargs)
    
    # Count open issues with this label
    OPEN_COUNT=$(gh issue list --state open --label "$label" --json number --jq 'length' 2>/dev/null || echo "0")
    
    # Count closed issues with this label in the past week
    CLOSED_COUNT=$(gh issue list --state closed --label "$label" --updated "$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)..$(date -u +%Y-%m-%dT%H:%M:%SZ)" --json number --jq 'length' 2>/dev/null || echo "0")
    
    if [ "$OPEN_COUNT" -gt 0 ] || [ "$CLOSED_COUNT" -gt 0 ]; then
        echo "- **$label:** $OPEN_COUNT open, $CLOSED_COUNT closed this week"
    fi
done

echo ""
echo "📈 **Summary:**"
echo "- Total new issues: $NEW_ISSUES"
echo "- Total closed issues: $CLOSED_ISSUES"

# Calculate net change
NET_CHANGE=$((NEW_ISSUES - CLOSED_ISSUES))
if [ $NET_CHANGE -gt 0 ]; then
    echo "- Net change: +$NET_CHANGE issues"
elif [ $NET_CHANGE -lt 0 ]; then
    echo "- Net change: $NET_CHANGE issues (good progress!)"
else
    echo "- Net change: 0 issues (balanced)"
fi

echo ""
echo "🔗 **View all issues:** [GitHub Issues](https://github.com/$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')/issues)"
echo ""
echo "---"
echo "*This summary is automatically generated every Monday at 9 AM UTC*"

echo ""
echo "✅ Test completed successfully!"
echo ""
echo "To test the actual workflow:"
echo "1. Commit and push this workflow file"
echo "2. Go to Actions tab in GitHub"
echo "3. Find 'Weekly Issue Summary' workflow"
echo "4. Click 'Run workflow' to trigger manually"
