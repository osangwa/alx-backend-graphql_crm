# Celery Setup for CRM Reports

This guide provides step-by-step instructions to set up Celery with Celery Beat for generating weekly CRM reports.

## Setup Steps

### 1. Install Redis and Dependencies

**Install Redis:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis