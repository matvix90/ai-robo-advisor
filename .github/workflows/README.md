# Weekly Issue Summary Workflow

This GitHub Actions workflow automatically generates and posts a weekly summary of repository issues to keep maintainers informed and improve backlog visibility.

> **Reference**: Based on the [GitHub samples models-in-actions weekly-issue-summary workflow](https://github.com/github-samples/models-in-actions/tree/main/workflows/weekly-issue-summary)

## Features

- **Automated Scheduling**: Runs every Monday at 9 AM UTC
- **Manual Triggering**: Can be triggered manually via GitHub Actions UI
- **Configurable Labels**: Track specific issue categories (bug, help wanted, triage, etc.)
- **Multiple Outputs**: Posts to GitHub Discussions and creates downloadable artifacts
- **Comprehensive Metrics**: Shows new/closed issues, label breakdowns, and net changes

## Configuration

### Environment Variables

The workflow uses these configurable environment variables:

- `LABELS_TO_INCLUDE`: Comma-separated list of labels to track (default: `bug,help wanted,triage,enhancement,question,documentation`)
- `POST_TO_DISCUSSION`: Whether to post summary to GitHub Discussions (default: `true`)
- `DISCUSSION_CATEGORY`: Discussion category for posting (default: `General`)

### Customization

To customize the workflow:

1. **Change Labels**: Edit the `LABELS_TO_INCLUDE` environment variable in the workflow file
2. **Change Schedule**: Modify the cron expression in the `on.schedule` section
3. **Disable Discussions**: Set `POST_TO_DISCUSSION` to `false`
4. **Add Slack Integration**: Add a new step to post to Slack webhook

## Usage

### Automatic Execution

The workflow runs automatically every Monday at 9 AM UTC. No action required.

### Manual Testing

1. Go to the **Actions** tab in your GitHub repository
2. Find the **Weekly Issue Summary** workflow
3. Click **Run workflow** to trigger manually
4. Check the workflow run for results

### Local Testing

Use the provided test script to verify the workflow logic locally:

```bash
./test-workflow.sh
```

**Prerequisites for local testing:**
- GitHub CLI (`gh`) installed and authenticated
- Repository access permissions

## Output

The workflow generates:

1. **GitHub Discussion Post**: Posted to the configured discussion category
2. **Artifact**: Downloadable markdown file with the summary
3. **Console Output**: Detailed metrics in the workflow logs

### Sample Output

```
📊 Weekly Issue Summary - 2024-01-15

📅 Period: 2024-01-08 to 2024-01-15

🆕 New Issues: 5
✅ Closed Issues: 3

🏷️ Issues by Label:
- bug: 2 open, 1 closed this week
- help wanted: 1 open, 0 closed this week
- enhancement: 2 open, 2 closed this week

📈 Summary:
- Total new issues: 5
- Total closed issues: 3
- Net change: +2 issues

🔗 View all issues: [GitHub Issues](https://github.com/owner/repo/issues)
```

## Permissions

The workflow requires these permissions:
- `issues: read` - To fetch issue data
- `discussions: write` - To post to discussions
- `contents: read` - To access repository information

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the workflow has the required permissions
2. **No Issues Found**: Check if the repository has issues and the date range is correct
3. **Discussion Post Failed**: Verify the discussion category exists and is accessible

### Debugging

- Check the workflow logs in the Actions tab
- Use the local test script to debug issues
- Verify GitHub CLI authentication and permissions

## Contributing

To improve this workflow:

1. Fork the repository
2. Make your changes
3. Test locally using the test script
4. Submit a pull request

## License

This workflow is part of the AI Robo-Advisor project and follows the same MIT license.
