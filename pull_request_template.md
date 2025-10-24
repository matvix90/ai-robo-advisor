# 🤖 Weekly Issue Summary Workflow

## 📋 Description

Implements an automated weekly issue summary workflow that posts aggregated issue counts and outstanding items to GitHub Discussions, keeping maintainers informed and improving backlog visibility.

## ✨ Features

- **📅 Automated Scheduling**: Runs every Monday at 9 AM UTC
- **🔧 Manual Triggering**: Can be triggered manually via GitHub Actions UI
- **🏷️ Configurable Labels**: Tracks specific issue categories (bug, help wanted, triage, etc.)
- **💬 Discussion Posts**: Automatically posts summaries to GitHub Discussions
- **📁 Downloadable Artifacts**: Creates markdown summaries for download
- **📊 Comprehensive Metrics**: Shows open/closed issues, completion rates, and label breakdowns

## 🎯 Acceptance Criteria

- ✅ File `.github/workflows/weekly-issue-summary.yml` added
- ✅ Runs on schedule (weekly) and generates a summary artifact or posts to configured destination
- ✅ Configurable set of labels to include in the summary (e.g., bug, help wanted, triage)
- ✅ Testing - Can be triggered manually to verify summary output

## 📁 Files Added/Modified

- `.github/workflows/weekly-issue-summary.yml` - Main workflow file
- `.github/workflows/README.md` - Comprehensive documentation
- `test-workflow.sh` - Local testing script

## 🔧 Configuration

The workflow uses these configurable environment variables:

- `LABELS_TO_INCLUDE`: Comma-separated list of labels to track (default: `bug,help wanted,triage,enhancement,question,documentation`)
- `POST_TO_DISCUSSION`: Whether to post summary to GitHub Discussions (default: `true`)
- `DISCUSSION_CATEGORY`: Discussion category for posting (default: `General`)

## 🧪 Testing

### Manual Testing
1. Go to Actions tab → "Weekly Issue Summary" workflow
2. Click "Run workflow" to trigger manually
3. Check results in Actions logs and Discussions

### Local Testing
```bash
./test-workflow.sh
```

## 📊 Sample Output

```
📊 Weekly Issue Summary - 2024-01-15

📅 Period: 2024-01-08 to 2024-01-15

📋 Open Issues: 5
✅ Closed Issues: 3
📊 Total Issues: 8

🏷️ Issues by Label:
- bug: 2 open, 1 closed
- help wanted: 1 open, 0 closed
- enhancement: 2 open, 2 closed

📈 Summary:
- Open issues: 5
- Closed issues: 3
- Total issues: 8
- Completion rate: 37%
```

## 🔗 Reference

Based on [GitHub samples models-in-actions weekly-issue-summary workflow](https://github.com/github-samples/models-in-actions/tree/main/workflows/weekly-issue-summary)

## 🚀 Ready for Review

This implementation meets all acceptance criteria and is ready for production use. The workflow will automatically keep maintainers informed with weekly issue summaries.

