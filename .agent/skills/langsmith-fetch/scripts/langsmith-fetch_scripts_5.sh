# 1. Try longer timeframe
langsmith-fetch traces --last-n-minutes 1440 --limit 50

# 2. Check environment
echo $LANGSMITH_API_KEY
echo $LANGSMITH_PROJECT

# 3. Try fetching threads instead
langsmith-fetch threads --limit 10

# 4. Verify tracing is enabled in your code
# Check for: LANGCHAIN_TRACING_V2=true