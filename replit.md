# Discord Points Store Bot

## Overview

A Discord bot that implements a virtual points-based economy system where users can earn and spend points on server rewards. The bot features a store system with purchasable items, approval workflows for purchases, and user balance management. Staff members can manage inventory, approve purchases, and administer user points through Discord commands.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py**: Uses the discord.py library with command extensions for handling Discord interactions
- **Command System**: Implements slash commands including `/setup` for initial server configuration
- **Interactive UI**: Utilizes Discord's UI components (buttons, views) for purchase approval workflows

### Data Storage
- **File-based Storage**: Uses JSON files for persistent data storage with server-specific separation
- **Guild-Specific Storage**: Each Discord server has its own data directory (`data/guild_{guild_id}/`)
- **Data Files** (per server):
  - `users.json`: Stores user point balances and transaction history for that server
  - `stock.json`: Contains available items, descriptions, and pricing for that server
  - `pending_purchases.json`: Tracks purchases awaiting staff approval for that server
  - `config.json`: Server-specific configuration (approval channel, role IDs, setup status)
- **Data Manager**: Guild-aware centralized class for handling all file operations and data integrity

### Configuration Management
- **Environment Variables**: Bot token stored as environment variable
- **Server Setup Command**: `/setup` command for configuring approval channel and role per server
- **Guild-Specific Config**: Each server stores its own approval channel ID, role ID, and setup status
- **Setup Validation**: Commands require server setup completion before use

### Purchase Workflow
- **Server-Specific Process**: Purchase approvals are sent to the configured approval channel for each server
- **Two-stage Process**: Users initiate purchases, then staff approve/deny through interactive buttons
- **Balance Verification**: Automatic checking of sufficient funds before purchase processing
- **Guild-Aware Approval**: Dedicated approval channel per server for staff to review purchase requests
- **Notification System**: DM notifications to users about purchase status updates with fallback to channel mentions

### Permission System
- **Multiple Permission Types**: 
  - Discord Administrator Permission: Full access to all commands
  - Specific Role ID: Custom role (1356586919483539619) with full staff permissions
  - Staff Role Names: Configurable role names in config.py (admin, administrator, moderator, staff, owner, manager, helper)
  - Regular users: Can view balance, shop, and make purchases
- **Staff Capabilities**: Give points, approve purchases, manage stock, and set user balances
- **Command Restrictions**: Different commands available based on user role permissions

### Error Handling
- **Graceful Failures**: Comprehensive error handling for file operations, Discord API calls, and user interactions
- **Fallback Mechanisms**: Alternative notification methods when DMs fail
- **Data Integrity**: File initialization and validation to prevent corruption

## External Dependencies

### Discord Platform
- **Discord API**: Core dependency for bot functionality and server integration
- **Discord.py Library**: Python wrapper for Discord API interactions
- **Bot Permissions**: Requires specific Discord permissions for message sending, user management, and role access

### Environment Configuration
- **DISCORD_BOT_TOKEN**: Required for bot authentication
- **Server-Specific Setup**: Each server configures its own approval channel and role through `/setup` command
- **No Global Configuration**: Approval channels and roles are set per-server, not globally through environment variables

### File System
- **Local Storage**: Relies on local file system for JSON data persistence
- **Data Directory**: Creates and manages `data/` directory for organized file storage

### Python Standard Library
- **JSON Module**: For data serialization and file operations
- **OS Module**: For environment variable access and file system operations
- **DateTime Module**: For timestamp tracking and time-based operations