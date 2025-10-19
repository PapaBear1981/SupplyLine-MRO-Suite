# Quick Update Guide

This guide shows you how to safely update the SupplyLine MRO Suite without losing data.

## 🚀 Quick Start (Recommended)

### Linux/Mac
```bash
chmod +x scripts/safe_update.sh
./scripts/safe_update.sh
```

### Windows (PowerShell)
```powershell
.\scripts\safe_update.ps1
```

That's it! The script handles everything automatically.

## ✅ What the Script Does

1. **Creates a backup** of your database
2. **Pulls latest code** from git
3. **Builds new containers** with latest changes
4. **Preserves your data** (never deletes volumes)
5. **Verifies everything works** before finishing

## ⚠️ Important Rules

### ✅ DO:
- Use the safe update script
- Use `docker-compose up -d --build` for manual updates
- Keep automatic backups enabled

### ❌ DON'T:
- **NEVER** use `docker-compose down -v` (deletes your data!)
- Don't skip backups before major changes
- Don't ignore health check failures

## 🔄 Manual Update (Advanced Users)

If you need manual control:

```bash
# 1. Create backup
cp database/tools.db database/backups/manual_$(date +%Y%m%d_%H%M%S).db

# 2. Pull changes
git pull

# 3. Update containers (IMPORTANT: No -v flag!)
docker-compose build --no-cache
docker-compose stop
docker-compose up -d

# 4. Verify
curl http://localhost:5000/api/health
```

## 🆘 If Something Goes Wrong

### Database is Empty After Update

1. Go to **Admin Dashboard** → **Database** tab
2. Find the most recent backup
3. Click **Restore**
4. Refresh the page

### Update Script Failed

1. Check the error message
2. Ensure Docker is running
3. Check disk space: `df -h`
4. Try manual update steps above

### Can't Access the Application

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

## 📚 More Information

For detailed information, see:
- [Database Persistence Guide](docs/DATABASE_PERSISTENCE.md)
- [Deployment Guide](DEPLOYMENT.md) (if available)

## 🔐 Backup Management

### Create Manual Backup
1. Admin Dashboard → Database tab
2. Click "Create Backup"

### Download Backup
1. Admin Dashboard → Database tab
2. Click download icon (⬇️) next to backup

### Restore Backup
1. Admin Dashboard → Database tab
2. Click restore icon (🔄) next to backup
3. Confirm restoration

## 📊 Health Monitoring

Check database health:
1. Admin Dashboard → Database tab
2. View health status and metrics

Or via command line:
```bash
curl http://localhost:5000/api/admin/database/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 Best Practices

1. **Always use the safe update script**
2. **Test in development first** if possible
3. **Create manual backup** before major changes
4. **Monitor disk space** for backup storage
5. **Keep automatic backups enabled**

## 📞 Need Help?

1. Check application logs: `docker-compose logs`
2. Review [Troubleshooting](docs/DATABASE_PERSISTENCE.md#troubleshooting)
3. Contact your system administrator

