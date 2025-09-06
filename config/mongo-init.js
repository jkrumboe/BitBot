// MongoDB initialization script
db = db.getSiblingDB('bitskins_bot');

// Create collections for each event type
db.createCollection('listed_items');
db.createCollection('price_changed_items');
db.createCollection('delisted_sold_items');

// Create indexes for listed_items collection
db.listed_items.createIndex({ "timestamp": 1 });
db.listed_items.createIndex({ "item_id": 1 });
db.listed_items.createIndex({ "item_name": 1 });
db.listed_items.createIndex({ "price_usd": 1 });
db.listed_items.createIndex({ "wear": 1 });
db.listed_items.createIndex({ "float_value": 1 });
db.listed_items.createIndex({ "skin_id": 1 });

// Create indexes for price_changed_items collection
db.price_changed_items.createIndex({ "timestamp": 1 });
db.price_changed_items.createIndex({ "item_id": 1 });
db.price_changed_items.createIndex({ "item_name": 1 });
db.price_changed_items.createIndex({ "new_price_usd": 1 });
db.price_changed_items.createIndex({ "price_change_percent": 1 });
db.price_changed_items.createIndex({ "wear": 1 });

// Create indexes for delisted_sold_items collection
db.delisted_sold_items.createIndex({ "timestamp": 1 });
db.delisted_sold_items.createIndex({ "item_id": 1 });
db.delisted_sold_items.createIndex({ "item_name": 1 });
db.delisted_sold_items.createIndex({ "price_usd": 1 });
db.delisted_sold_items.createIndex({ "reason": 1 });
db.delisted_sold_items.createIndex({ "wear": 1 });

print('Database initialized with all collections and indexes');
