# Database Persistence and Backup Guide

This guide explains how the SupplyLine MRO Suite ensures database persistence during updates and provides comprehensive backup and restore capabilities.

## Table of Contents

1. [Overview](#overview)
2. [Database Configuration](#database-configuration)
3. [Automatic Backups](#automatic-backups)
4. [Manual Backups](#manual-backups)
5. [Safe Update Process](#safe-update-process)
6. [Restore Procedures](#restore-procedures)
7. [Troubleshooting](#troubleshooting)

## Overview

The application uses **SQLite** as its default database, stored in a Docker volume to ensure persistence across container updates. The system includes:

- **Automatic scheduled backups** (configurable interval)
- **Manual backup/restore** via admin UI
- **Safe update scripts** that preserve data
- **Database health monitoring**
- **Backup rotation** to manage disk space

## Database Configuration

### SQLite (Default)

The database is stored at `database/tools.db` and mounted as a Docker volume:

```yaml
volumes:
  database:
    name: supplyline-database
```

**Advantages:**
- Zero configuration
- Excellent performance for MRO workloads
- Simple backup (single file)
- No additional services required

### PostgreSQL (Optional)

For high-concurrency environments, you can switch to PostgreSQL by setting:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

## Automatic Backups

### Configuration

Configure automatic backups in your `.env` file:

```bash
# Enable automatic backups (default: true)
AUTO_BACKUP_ENABLED=true

# Backup interval in hours (default: 24)
AUTO_BACKUP_INTERVAL_HOURS=24

# Create backup on startup (default: true)
BACKUP_ON_STARTUP=true

# Maximum backups to keep (default: 10)
MAX_DATABASE_BACKUPS=10

# Compress backups (default: true)
COMPRESS_BACKUPS=true
```

### How It Works

1. **Startup Backup**: When the application starts, it creates a backup labeled `startup_YYYYMMDD_HHMMSS.db`
2. **Scheduled Backups**: Every 24 hours (configurable), a backup labeled `scheduled_YYYYMMDD_HHMMSS.db` is created
3. **Rotation**: Old backups are automatically deleted when the count exceeds `MAX_DATABASE_BACKUPS`
4. **Compression**: Backups are compressed with gzip to save disk space (reduces size by ~70%)

### Backup Location

Backups are stored in:
- **Local**: `database/backups/`
- **Docker**: `/database/backups/` (inside container)

## Manual Backups

### Via Admin UI

1. Navigate to **Admin Dashboard** → **Database** tab
2. Click **Create Backup** button
3. Download, restore, or delete backups from the table

### Via API

Create a backup:
```bash
curl -X POST http://localhost:5000/api/admin/database/backup \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"compress": true}'
```

List backups:
```bash
curl http://localhost:5000/api/admin/database/backups \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Safe Update Process

### Using the Safe Update Script

**Linux/Mac:**
```bash
chmod +x scripts/safe_update.sh
./scripts/safe_update.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\safe_update.ps1
```

### What the Script Does

1. ✅ **Creates a pre-update backup** of the database
2. ✅ **Pulls latest code** from git (if applicable)
3. ✅ **Builds new Docker images** with `--no-cache`
4. ✅ **Stops containers** (preserves volumes!)
5. ✅ **Starts updated containers**
6. ✅ **Verifies health** of backend and frontend
7. ✅ **Cleans up old images**

### Manual Update (Advanced)

If you prefer manual control:

```bash
# 1. Create backup
cp database/tools.db database/backups/manual_backup_$(date +%Y%m%d_%H%M%S).db

# 2. Pull latest changes
git pull

# 3. Rebuild and restart (IMPORTANT: No -v flag!)
docker-compose build --no-cache
docker-compose stop
docker-compose up -d

# 4. Verify health
curl http://localhost:5000/api/health
```

**⚠️ NEVER USE:** `docker-compose down -v` (this deletes volumes!)

## Restore Procedures

### Via Admin UI

1. Navigate to **Admin Dashboard** → **Database** tab
2. Find the backup you want to restore
3. Click the **Restore** button (🔄 icon)
4. Confirm the restoration
5. A safety backup is created automatically before restore
6. Refresh the page after restoration

### Via API

```bash
curl -X POST http://localhost:5000/api/admin/database/restore \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_filename": "backup_20240101_120000.db.gz",
    "create_backup_before_restore": true
  }'
```

### Manual Restore

```bash
# 1. Stop the application
docker-compose stop

# 2. Replace the database
cp database/backups/backup_20240101_120000.db database/tools.db

# 3. Start the application
docker-compose up -d
```

## Database Health Monitoring

### Via Admin UI

The **Database** tab shows:
- ✅ Health status (integrity check)
- 📊 Database size
- 📋 Table count
- 💾 Number of backups

### Via API

```bash
curl http://localhost:5000/api/admin/database/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "success": true,
  "healthy": true,
  "message": "Database is healthy",
  "details": {
    "integrity_check": "ok",
    "size_mb": 15.42,
    "table_count": 23,
    "page_count": 3947,
    "page_size": 4096
  }
}
```

## Troubleshooting

### Database Lost After Update

**Cause**: Used `docker-compose down -v` which deletes volumes

**Solution**:
1. Check if a backup exists in `database/backups/`
2. Restore the most recent backup via Admin UI
3. Always use the safe update script in the future

### Backup Failed

**Possible Causes**:
- Disk space full
- Permission issues
- Database locked

**Solutions**:
```bash
# Check disk space
df -h

# Check backup directory permissions
ls -la database/backups/

# Check database file permissions
ls -la database/tools.db

# Manually create backup directory
mkdir -p database/backups
chmod 755 database/backups
```

### Restore Failed

**Possible Causes**:
- Corrupted backup file
- Incompatible database version
- Application still running

**Solutions**:
1. Verify backup integrity via Admin UI (health check)
2. Stop the application before manual restore
3. Try an older backup if current one is corrupted

### Automatic Backups Not Running

**Check**:
1. Verify `AUTO_BACKUP_ENABLED=true` in `.env`
2. Check application logs: `docker-compose logs backend | grep backup`
3. Restart the application: `docker-compose restart backend`

### Out of Disk Space

**Solution**:
1. Reduce `MAX_DATABASE_BACKUPS` in `.env`
2. Manually delete old backups via Admin UI
3. Enable compression: `COMPRESS_BACKUPS=true`

## Best Practices

1. **Always use the safe update script** for updates
2. **Enable automatic backups** for peace of mind
3. **Test restores periodically** to ensure backups work
4. **Download critical backups** to external storage
5. **Monitor disk space** if you have many backups
6. **Keep at least 7 days** of backups (adjust `MAX_DATABASE_BACKUPS`)
7. **Create manual backup** before major changes

## Backup Schedule Recommendations

| Environment | Interval | Retention |
|-------------|----------|-----------|
| Development | 24 hours | 5 backups |
| Staging     | 12 hours | 10 backups |
| Production  | 6 hours  | 20 backups |

## Security Notes

- Backups contain **all data** including user information
- Store backups securely with appropriate access controls
- Downloaded backups should be encrypted if stored externally
- Only admins can create, restore, or delete backups
- All backup operations are logged in the audit log

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review application logs: `docker-compose logs backend`
3. Check database health via Admin UI
4. Contact your system administrator

