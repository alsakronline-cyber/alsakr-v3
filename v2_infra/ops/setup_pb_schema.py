import httpx
import asyncio
import os
import sys

# Internal URL inside docker network
PB_URL = "http://pocketbase:8090"
ADMIN_EMAIL = "admin@alsakronline.com"
ADMIN_PASS = "password123"

async def create_collection(client, token, name, schema, rules=None):
    print(f"Syncing collection {name}...")
    headers = {"Authorization": token}
    
    # Default rules
    if rules is None:
        rules = {
            "listRule": "",
            "viewRule": "",
            "createRule": "",
            "updateRule": "",
            "deleteRule": ""
        }

    # Check if exists
    resp = await client.get(f"{PB_URL}/api/collections/{name}", headers=headers)
    exists = resp.status_code == 200
    
    data = {
        "name": name,
        "type": "base",
        "schema": schema,
        **rules
    }

    if exists:
        # Update existing
        resp = await client.patch(f"{PB_URL}/api/collections/{name}", json=data, headers=headers)
        if resp.status_code == 200:
            print(f"  - Updated successfully.")
        else:
            print(f"  - Update failed: {resp.status_code} {resp.text}")
    else:
        # Create new
        resp = await client.post(f"{PB_URL}/api/collections", json=data, headers=headers)
        if resp.status_code == 200:
            print(f"  - Created successfully.")
        else:
            print(f"  - Creation failed: {resp.status_code} {resp.text}")

async def main():
    print("Starting PB System-Wide Schema Setup...")
    async with httpx.AsyncClient() as client:
        # Auth
        try:
            url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
            resp = await client.post(url, json={
                "identity": ADMIN_EMAIL, "password": ADMIN_PASS
            })
            
            if resp.status_code == 404:
                url = f"{PB_URL}/api/admins/auth-with-password"
                resp = await client.post(url, json={
                    "identity": ADMIN_EMAIL, "password": ADMIN_PASS
                })

            if resp.status_code != 200:
                print(f"Admin auth failed ({resp.status_code}): {resp.text}")
                return
            token = resp.json()["token"]
            print("Admin authenticated.")
        except Exception as e:
            print(f"Connection error to {PB_URL}: {e}")
            return

        # 1. Inquiries
        await create_collection(client, token, "inquiries", [
            {"name": "buyer_id", "type": "text", "required": True},
            {"name": "products", "type": "json", "required": True},
            {"name": "message", "type": "text"},
            {"name": "status", "type": "select", "options": ["pending", "quoted", "processed", "closed"]}
        ])

        # 2. Quotations
        await create_collection(client, token, "quotations", [
            {"name": "inquiry_id", "type": "text", "required": True},
            {"name": "vendor_id", "type": "text", "required": True},
            {"name": "items", "type": "json"},
            {"name": "total_price", "type": "number"},
            {"name": "currency", "type": "text"},
            {"name": "valid_until", "type": "date"},
            {"name": "notes", "type": "text"},
            {"name": "status", "type": "select", "options": ["pending", "accepted", "rejected", "expired"]}
        ])

        # 3. Messages
        await create_collection(client, token, "messages", [
            {"name": "inquiry_id", "type": "text", "required": True},
            {"name": "sender_id", "type": "text"},
            {"name": "sender_role", "type": "select", "options": ["buyer", "vendor"]},
            {"name": "content", "type": "text"},
            {"name": "read", "type": "bool"}
        ])

        # 4. Vendor Stock
        await create_collection(client, token, "vendor_stock", [
            {"name": "vendor_id", "type": "text", "required": True},
            {"name": "part_number", "type": "text", "required": True},
            {"name": "custom_price", "type": "number"},
            {"name": "stock_quantity", "type": "number"}
        ])

        # 5. Vendor Profiles
        await create_collection(client, token, "vendor_profiles", [
            {"name": "user_id", "type": "text", "required": True},
            {"name": "brands", "type": "json"},
            {"name": "categories", "type": "json"},
            {"name": "rating", "type": "number"},
            {"name": "cr_number", "type": "text"},
            {"name": "sector", "type": "text"},
            {"name": "location", "type": "text"},
            {"name": "verification_status", "type": "select", "options": ["pending", "verified", "rejected"]}
        ])

        # 6. Conversations (AI History)
        await create_collection(client, token, "conversations", [
            {"name": "user_id", "type": "text", "required": True},
            {"name": "messages", "type": "json"},
            {"name": "summary", "type": "text"}
        ])

if __name__ == "__main__":
    asyncio.run(main())
