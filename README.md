# Job Summary Test

Simple test to validate job summary figure generation without running long CFD tests.

## How it works

1. **Workflow unzips a pre-made artifact** (llm-test-results-26988984471.zip)
2. **Creates individual preview artifacts** from the images
3. **Tests the job summary logic** to see if it can find and link the artifacts

## Quick test

1. Push to GitHub
2. Run workflow manually via GitHub Actions
3. Check the job summary page to see if figures display correctly

This lets you iterate on the job summary logic in ~30 seconds instead of waiting 15+ minutes for CFD tests.
