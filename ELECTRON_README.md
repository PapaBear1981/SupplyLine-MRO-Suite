# SupplyLine MRO Suite - Electron Desktop Application

This document describes the Electron desktop application version of SupplyLine MRO Suite with Supabase integration for data synchronization and offline capabilities.

## Features

- **Desktop Application**: Native desktop app using Electron
- **Supabase Integration**: Cloud database synchronization
- **Offline Mode**: Local data storage with IndexedDB
- **Data Synchronization**: Automatic sync between local and cloud data
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Architecture

### Components

1. **Electron Main Process** (`electron/main.js`)
   - Application lifecycle management
   - Window creation and management
   - Backend server integration
   - Auto-updater functionality

2. **Electron Preload Script** (`electron/preload.js`)
   - Secure IPC communication bridge
   - Exposes safe APIs to renderer process

3. **Supabase Service** (`src/services/supabase.js`)
   - Supabase client management
   - Database operations
   - Real-time subscriptions

4. **Sync Service** (`src/services/syncService.js`)
   - Offline/online data synchronization
   - Conflict resolution
   - Queue management for pending operations

5. **Offline Storage** (`src/utils/offlineStorage.js`)
   - IndexedDB wrapper for local data storage
   - Data persistence and retrieval

## Setup Instructions

### 1. Install Dependencies

```bash
# Install root dependencies (Electron)
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Set Up Supabase Database

Run the setup script to create your Supabase database:

```bash
node setup-supabase.js
```

This will:
- Prompt for your Supabase URL and service role key
- Create the necessary database tables
- Set up a default admin user (ADMIN001/admin123)

### 3. Development Mode

To run the application in development mode:

```bash
# Start both frontend and backend servers, then launch Electron
npm run electron-dev
```

Or start components separately:

```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Start Electron
npm run electron
```

### 4. Production Build

To build the application for distribution:

```bash
# Build for current platform
npm run dist

# Build for specific platforms
npm run dist:win    # Windows
npm run dist:mac    # macOS
npm run dist:linux  # Linux
```

## Configuration

### Supabase Configuration

When you first run the Electron app, you'll be prompted to configure Supabase:

1. **Supabase URL**: Your project URL (e.g., `https://your-project.supabase.co`)
2. **API Key**: Your anon/public API key (not the service role key)

The configuration is stored securely using `electron-store`.

### Environment Variables

For web deployment, you can also use environment variables:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## Data Synchronization

### How It Works

1. **Local Storage**: All data is stored locally using IndexedDB
2. **Online Sync**: When online, data syncs automatically with Supabase
3. **Conflict Resolution**: Configurable conflict resolution strategies
4. **Queue Management**: Offline operations are queued and synced when online

### Sync Strategies

- **Server Wins**: Remote data takes precedence (default)
- **Client Wins**: Local data takes precedence
- **Manual**: User resolves conflicts manually

### Monitoring Sync Status

The application provides real-time sync status:
- Online/offline indicator
- Last sync timestamp
- Pending operations count
- Sync errors and warnings

## Database Schema

The Supabase database mirrors the SQLite schema with PostgreSQL enhancements:

- **Users**: User accounts and authentication
- **Tools**: Tool inventory and management
- **Checkouts**: Tool checkout/return tracking
- **Chemicals**: Chemical inventory management
- **Audit Log**: Activity tracking and auditing
- **Calibrations**: Tool calibration records
- **Cycle Counts**: Inventory cycle counting

## Security

### Row Level Security (RLS)

Supabase RLS policies ensure:
- Users can only access their own data
- Admins have elevated permissions
- Data isolation between organizations

### API Key Management

- API keys are stored securely using Electron's secure storage
- Service role keys are never exposed to the client
- All database operations use appropriate permission levels

## Troubleshooting

### Common Issues

1. **Supabase Connection Failed**
   - Verify URL and API key are correct
   - Check network connectivity
   - Ensure Supabase project is active

2. **Sync Not Working**
   - Check online status
   - Verify Supabase configuration
   - Review sync service logs

3. **Data Not Appearing**
   - Force a manual sync
   - Check local storage in browser dev tools
   - Verify database permissions

### Debug Mode

Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## Migration from SQLite

To migrate existing SQLite data to Supabase:

1. Run the setup script: `node setup-supabase.js`
2. Use the migration script: `node scripts/migrate-to-supabase.js`
3. Verify data integrity in Supabase dashboard

## Deployment

### Auto-Updates

The application includes auto-updater functionality:
- Checks for updates on startup
- Downloads and installs updates automatically
- Notifies users of available updates

### Distribution

Built applications can be distributed via:
- Direct download from releases
- App stores (with additional configuration)
- Enterprise deployment tools

## Development

### Adding New Features

1. **Database Changes**: Update both SQLite and Supabase schemas
2. **Sync Logic**: Add sync support for new data types
3. **Offline Support**: Ensure features work offline
4. **Testing**: Test sync scenarios and conflict resolution

### Testing

```bash
# Run frontend tests
cd frontend
npm test

# Run backend tests
cd backend
python -m pytest

# Test Electron app
npm run test
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check Supabase dashboard for database issues
4. Create an issue in the project repository
