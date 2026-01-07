#!/bin/bash
# Local Push Script - Run this on your local machine

BRANCH="v2-industrial-ai"

echo "Adding changes..."
git add .

echo "Enter commit message (default: Update Phase 3 implementation):"
read msg
if [ -z "$msg" ]; then
    msg="Update Phase 3 implementation"
fi

echo "Committing..."
git commit -m "$msg"

echo "Pushing to origin $BRANCH..."
git push origin $BRANCH

echo "Done! Now go to your VPS and run: cd alsakr_v2/v2_infra && bash deploy.sh"
