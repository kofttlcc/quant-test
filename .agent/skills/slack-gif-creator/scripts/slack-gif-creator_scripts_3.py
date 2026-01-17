from core.validators import validate_dimensions

# Check dimensions
passes, info = validate_dimensions(128, 128, is_emoji=True)
# Returns: (True/False, dict with dimension details)