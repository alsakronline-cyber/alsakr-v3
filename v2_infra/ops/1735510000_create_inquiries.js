migrate((db) => {
    const collection = new Collection({
        "name": "inquiries",
        "type": "base",
        "schema": [
            { "name": "buyer_id", "type": "text", "required": true },
            { "name": "products", "type": "json", "required": true },
            { "name": "message", "type": "text" },
            { "name": "status", "type": "select", "options": ["pending", "quoted", "processed", "closed"] }
        ],
        "listRule": "",
        "viewRule": "",
        "createRule": "",
        "updateRule": "",
        "deleteRule": null
    });

    return Dao(db).saveCollection(collection);
}, (db) => {
    const dao = new Dao(db);
    const collection = dao.findCollectionByNameOrId("inquiries");

    return dao.deleteCollection(collection);
})
