import math
import smtplib
import os
import logging
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
from inventoryService import InventoryService
from amzService2 import getSales
from asinNameUtil import asinNames
from dotenv import load_dotenv

load_dotenv()


def get_weekly_sales():
    end = date.today() - timedelta(days=1)   # yesterday
    start = end - timedelta(days=6)          # 7 days back
    rows = []
    for asin, name in asinNames.items():
        df = getSales(asin, start, end, 'Day')
        if df is not None and not df.empty and 'unitCount' in df.columns:
            rows.append({
                'ASIN': asin,
                'Product': name,
                'Units Sold': int(df['unitCount'].sum()),
                'Revenue': df['totalSales.amount'].sum()
            })
    return pd.DataFrame(rows).sort_values('Revenue', ascending=False)


def send_weekly_email():
    logging.info('Kicking off the email function...')
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Weekly Amazon Report - {datetime.now().strftime('%B %d, %Y')}"

    # --- Sales section ---
    logging.info('Retrieving last 7 days of sales...')
    sales_df = get_weekly_sales()
    sales_df['Revenue'] = sales_df['Revenue'].apply(lambda x: f'${x:,.2f}')
    sales_html = sales_df.to_html(index=False, table_id="sales-table")

    # --- Replenishment section ---
    logging.info('Retrieving inventory...')
    inventoryService = InventoryService()
    inv_df = inventoryService.getInventoryNeeds()
    inv_df['Product'] = inv_df['ASIN'].map(asinNames)


    # Say a product has 3.2 weeks on hand and sells 15 units/week on average and we are targeting 6 weeks on hand:
    # 6 - 3.2 = 2.8 — weeks of stock needed to reach 6 weeks
    # 2.8 * 15 = 42 — raw units needed
    # 42 / 10 = 4.2 — divide by 10 (because you ship in cases of 10)
    # ceil(4.2) = 5 — round up so you don't under-order
    # 5 * 10 = 50 — multiply back to get actual units
    # Result: order 50 units (5 cases of 10) to bring inventory from 3.2 weeks up to ~6 weeks.
    restock_df = inv_df[inv_df['Weeks On Hand'] < 6].copy()
    restock_df['Suggested Order'] = (
        ((6 - restock_df['Weeks On Hand']) * restock_df['Week Average'] / 10)
        .apply(math.ceil) * 10
    ).astype(int)
    restock_df = restock_df[['ASIN', 'Product', 'Weeks On Hand', 'Week Average', 'Suggested Order']]

    if restock_df.empty:
        restock_html = '<p style="color: green;">&#10003; All products are well-stocked (6+ weeks on hand).</p>'
    else:
        restock_html = restock_df.to_html(index=False, table_id="restock-table")

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            h2 {{ color: #333; border-bottom: 2px solid #ddd; padding-bottom: 6px; }}
        </style>
    </head>
    <body>
        <h2>Sales &mdash; Last 7 Days</h2>
        {sales_html}
        <h2>Replenishment Needed (&lt;6 Weeks On Hand)</h2>
        {restock_html}
    </body>
    </html>
    """

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
        print(f"Error sending email: {e}")
        logging.error(f"Error sending email: {e}")


if __name__ == "__main__":
    print("Testing email function directly...")
    send_weekly_email()
    print("Direct test complete")
