# Celery Setup for CRM Reports

This guide explains how to set up Celery with Celery Beat for generating weekly CRM reports in the Django CRM application.

## Prerequisites

- Python 3.8+
- Django 3.2+
- Redis server
- Existing Django CRM project with GraphQL endpoints

## Installation Steps

### 1. Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# Or install individually if needed
pip install celery django-celery-beat redis requests gql[requests]