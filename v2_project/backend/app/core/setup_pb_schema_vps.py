import httpx
import asyncio
import os
import sys

# Internal URL inside docker network
PB_URL = os.getenv("PB_URL", "http://pocketbase:8090")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@alsakronline.com")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "password123")

async def create_collection(client, token, name, schema, rules=None, type="base"):
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
    
    if exists:
        # Patch existing - we don't send type for patch to avoid issues
        existing_data = resp.json()
        data = {
            "name": name,
            "schema": schema,
            **rules
        }
        resp = await client.patch(f"{PB_URL}/api/collections/{name}", json=data, headers=headers)
        if resp.status_code == 200:
            print(f"  - Updated successfully.")
        else:
            print(f"  - Update failed: {resp.status_code} {resp.text}")
    else:
        # Create new
        data = {
            "name": name,
            "type": type,
            "schema": schema,
            **rules
        }
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
            print(f"Attempting auth at: {url}")
            
            # Credentials to try
            creds_list = [
                {"identity": "admin@alsakronline.com", "password": "#Anas231#Bkar3110"},
                {"identity": ADMIN_EMAIL, "password": ADMIN_PASS},
                {"identity": "developer@alsakronline.com", "password": "password12345"}
            ]
            
            token = None
            for creds in creds_list:
                print(f"Trying identity: {creds.get('identity') or creds.get('email')}")
                resp = await client.post(url, json=creds, timeout=5.0)
                
                if resp.status_code == 200:
                    token = resp.json()["token"]
                    print("Admin authenticated.")
                    break
                else:
                    print(f"  - Failed ({resp.status_code}): {resp.text}")
            
            if not token:
                # Try legacy admins endpoint
                url_legacy = f"{PB_URL}/api/admins/auth-with-password"
                print(f"Retrying legacy endpoint: {url_legacy}")
                for creds in creds_list:
                    resp = await client.post(url_legacy, json=creds, timeout=5.0)
                    if resp.status_code == 200:
                        token = resp.json()["token"]
                        print("Admin authenticated (legacy).")
                        break
            
            if not token:
                print(f"CRITICAL: All admin auth attempts failed.")
                return

        except Exception as e:
            print(f"Connection error to {PB_URL}: {e}")
            return

        # 0. Users (Patch existing auth collection)
        await create_collection(client, token, "users", [
            {"name": "name", "type": "text"},
            {"name": "company", "type": "text"},
            {"name": "phone", "type": "text"},
            {"name": "jobTitle", "type": "text"},
            {"name": "country", "type": "text"},
            {"name": "role", "type": "select", "options": ["admin", "vendor", "buyer"]}
        ])

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

        # 7. Products (Reference Collection)
        await create_collection(client, token, "products", [
            {"name": "part_number", "type": "text", "required": True},
            {"name": "name", "type": "text"},
            {"name": "category", "type": "text"},
            {"name": "url", "type": "text"},
            {"name": "image_url", "type": "text"},
            {"name": "pdf_url", "type": "text"},
            {"name": "description", "type": "text"}
        ])

if __name__ == "__main__":
    asyncio.run(main())
