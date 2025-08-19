# Discord Points Store Bot

## Overview

A Discord bot that implements a virtual points-based economy system where users can earn and spend points on server rewards. The bot features a store system with purchasable items, approval workflows for purchases, and user balance management. Staff members can manage inventory, approve purchases, and administer user points through Discord commands.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py**: Uses the discord.py library with command extensions for handling Discord interactions
- **Command System**: Implements slash commands and traditional prefix commands (!command) for user interactions
- **Interactive UI**: Utilizes Discord's UI components (buttons, views) for purchase approval workflows

### Data Storage
- **File-based Storage**: Uses JSON files for persistent data storage instead of a database
- **Data Files**:
  - `users.json`: Stores user point balances and transaction history
  - `stock.json`: Contains available items, descriptions, and pricing
  - `pending_purchases.json`: Tracks purchases awaiting staff approval
- **Data Manager**: Centralized class for handling all file operations and data integrity

### Configuration Management
- **Environment Variables**: Bot token and channel/role IDs stored as environment variables
- **Role-based Permissions**: Configurable admin and staff roles for different permission levels
- **Validation System**: Built-in configuration validation to ensure proper setup

### Purchase Workflow
- **Two-stage Process**: Users initiate purchases, then staff approve/deny through interactive buttons
- **Balance Verification**: Automatic checking of sufficient funds before purchase processing
- **Approval Channel**: Dedicated channel for staff to review and process purchase requests
- **Notification System**: DM notifications to users about purchase status updates

### Permission System
- **Role Hierarchy**: 
  - Admin roles: Full system access and user management
  - Staff roles: Can approve purchases and basic moderation
  - Regular users: Can view balance, shop, and make purchases
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
- **APPROVAL_CHANNEL_ID**: Channel where purchase requests are sent for staff review
- **APPROVAL_ROLE_ID**: Optional role ID for purchase approval permissions

### File System
- **Local Storage**: Relies on local file system for JSON data persistence
- **Data Directory**: Creates and manages `data/` directory for organized file storage

### Python Standard Library
- **JSON Module**: For data serialization and file operations
- **OS Module**: For environment variable access and file system operations
- **DateTime Module**: For timestamp tracking and time-based operations