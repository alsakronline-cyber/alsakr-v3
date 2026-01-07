#!/bin/bash
# Al Sakr Online - Schema Sync Script

echo "🔄 Syncing PocketBase Schema..."

# Run the setup script inside the backend container
docker exec alsakr-backend python3 -m app.core.setup_pb_schema_vps

if [ $? -eq 0 ]; then
    echo "✅ Schema sync complete!"
else
    echo "❌ Schema sync failed."
    exit 1
fi
