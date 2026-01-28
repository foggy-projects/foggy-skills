# MySQL Operations Reference

Common MySQL operations and patterns for database migrations and modifications.

## Table of Contents
- [DDL Operations](#ddl-operations)
- [Data Migration Patterns](#data-migration-patterns)
- [Index Management](#index-management)
- [Common Troubleshooting](#common-troubleshooting)

## DDL Operations

### Create Table

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Add Column

```sql
-- Add single column
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;

-- Add with default value
ALTER TABLE users ADD COLUMN status TINYINT DEFAULT 1 COMMENT 'User status';

-- Add multiple columns
ALTER TABLE users
    ADD COLUMN last_login TIMESTAMP NULL,
    ADD COLUMN login_count INT DEFAULT 0;
```

### Modify Column

```sql
-- Change column type
ALTER TABLE users MODIFY COLUMN username VARCHAR(100);

-- Change column name and type
ALTER TABLE users CHANGE COLUMN phone mobile_phone VARCHAR(20);

-- Change with constraint
ALTER TABLE users MODIFY COLUMN email VARCHAR(100) NOT NULL UNIQUE;
```

### Drop Column

```sql
ALTER TABLE users DROP COLUMN phone;
```

### Add Index

```sql
-- Single column index
CREATE INDEX idx_username ON users(username);

-- Composite index
CREATE INDEX idx_user_status ON users(username, status);

-- Unique index
CREATE UNIQUE INDEX uk_email ON users(email);
```

### Drop Index

```sql
DROP INDEX idx_username ON users;
```

## Data Migration Patterns

### Safe Column Migration

```sql
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN new_status VARCHAR(20);

-- Step 2: Migrate data
UPDATE orders SET new_status =
    CASE old_status
        WHEN 1 THEN 'pending'
        WHEN 2 THEN 'completed'
        WHEN 3 THEN 'cancelled'
    END;

-- Step 3: Verify migration
SELECT old_status, new_status, COUNT(*)
FROM orders
GROUP BY old_status, new_status;

-- Step 4: Make new column NOT NULL
ALTER TABLE orders MODIFY COLUMN new_status VARCHAR(20) NOT NULL;

-- Step 5: Drop old column (after verification)
ALTER TABLE orders DROP COLUMN old_status;
```

### Batch Update Pattern

For large tables, update in batches to avoid locking:

```sql
-- Update in batches of 1000
SET @batch_size = 1000;
SET @offset = 0;

REPEAT
    UPDATE orders
    SET processed = 1
    WHERE processed = 0
    LIMIT @batch_size;

    SET @offset = @offset + @batch_size;
UNTIL ROW_COUNT() = 0 END REPEAT;
```

### Copy Table Structure

```sql
-- Copy structure only
CREATE TABLE users_backup LIKE users;

-- Copy structure and data
CREATE TABLE users_backup AS SELECT * FROM users;
```

## Index Management

### Check Existing Indexes

```sql
SHOW INDEX FROM users;

-- Or detailed view
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    INDEX_TYPE,
    NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'your_database'
    AND TABLE_NAME = 'users';
```

### Analyze Index Usage

```sql
-- Check unused indexes
SELECT * FROM sys.schema_unused_indexes
WHERE object_schema = 'your_database';

-- Check redundant indexes
SELECT * FROM sys.schema_redundant_indexes
WHERE table_schema = 'your_database';
```

### Add Missing Foreign Keys

```sql
ALTER TABLE orders
ADD CONSTRAINT fk_user_id
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE ON UPDATE CASCADE;
```

## Common Troubleshooting

### Connection Issues

```bash
# Test connection
docker run --rm -it mysql:8.0 \
  mysql -h<host> -P<port> -u<user> -p<password> -e "SELECT 1"
```

### Check Table Status

```sql
-- Table size and rows
SELECT
    TABLE_NAME,
    TABLE_ROWS,
    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS 'Data Size (MB)',
    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS 'Index Size (MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'your_database'
ORDER BY DATA_LENGTH DESC;
```

### Character Set Issues

```sql
-- Check table charset
SHOW CREATE TABLE users;

-- Convert table charset
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Lock Issues

```sql
-- Show running transactions
SELECT * FROM information_schema.INNODB_TRX;

-- Show locks
SELECT * FROM information_schema.INNODB_LOCKS;

-- Kill blocking query
KILL <process_id>;
```

### Duplicate Key Errors

```sql
-- Find duplicates before adding unique constraint
SELECT username, COUNT(*)
FROM users
GROUP BY username
HAVING COUNT(*) > 1;

-- Remove duplicates (keep oldest)
DELETE u1 FROM users u1
INNER JOIN users u2
WHERE u1.id > u2.id AND u1.username = u2.username;
```

## Best Practices

1. **Always backup before DDL**: Use `CREATE TABLE backup AS SELECT * FROM original`
2. **Test on staging first**: Never run untested migrations on production
3. **Use transactions for data changes**: Wrap multiple DML in BEGIN/COMMIT
4. **Monitor long-running queries**: Set statement timeout
5. **Avoid SELECT * in production**: Specify columns explicitly
6. **Use prepared statements**: Prevent SQL injection
7. **Index foreign keys**: Improve join performance
8. **Regular ANALYZE TABLE**: Keep statistics updated
