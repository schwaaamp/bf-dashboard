import schedule
import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from inventoryService import InventoryService
from dotenv import load_dotenv
import os
import logging


load_dotenv()  # loads variables from .env into environment


def send_weekly_email():
    logging.info('Kicking off the email function...')
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Inventory report - {datetime.now().strftime('%B %d, %Y')}"
    
    logging.info('Retrieving inventory for the email...')
    inventoryService = InventoryService()
    inventoryDf = inventoryService.getInventoryNeeds()
    
    logging.info('Inventory results: ')
    logging.info(inventoryDf)
    df_html = inventoryDf.to_html(index=False, table_id="data-table")

    # Combine heading and table into one HTML message body
    html_body = f"""
    <html>
    <body>
        <p>Inventory needs as of {datetime.now().strftime('%B %d, %Y')}:</p>
        {df_html}
    </body>
    </html>
    """

    # Attach combined HTML
    message.attach(MIMEText(html_body, "html"))
    
    try:
        logging.info('Sending the email...')
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print(f"Email sent at {datetime.now()}")
    except Exception as e:
        print(f"Error: {e}")

# Schedule for every Monday at 9:00 AM
# Commented out in place of a cron job to handle this
"""
schedule.every().monday.at("7:00").do(send_weekly_email)

while True:
    schedule.run_pending()
    time.sleep(3000)  # Check every hour
 
# Test the function directly without scheduling
if __name__ == "__main__":
    print("Testing email function directly...")
    send_weekly_email()
    print("Direct test complete")
"""