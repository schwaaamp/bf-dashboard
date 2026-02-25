import sys
sys.path.insert(0, '/etc/secrets')

from email_service import send_weekly_email

print('sending the weekly inventory email...')
send_weekly_email()