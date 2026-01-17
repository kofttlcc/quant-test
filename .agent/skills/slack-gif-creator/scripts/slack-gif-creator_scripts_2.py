from core.validators import check_slack_size

# Check if GIF meets size limits
passes, info = check_slack_size('emoji.gif', is_emoji=True)
# Returns: (True/False, dict with size details)