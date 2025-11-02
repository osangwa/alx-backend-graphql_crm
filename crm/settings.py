INSTALLED_APPS = [
    # ... other apps
    'django_crontab',
]

# Cron job configuration
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]