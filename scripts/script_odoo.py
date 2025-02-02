import xmlrpc.client
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from utils import insert_or_update_contacts, insert_or_update_factures, delete_old_records

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
API_ODOO = os.getenv("API_ODOO")


# Authentification
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

if uid:
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
else:
    raise Exception("Échec de l'authentification à Odoo")

# handel contacts from odoo db
contacts = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search_read", [[]], {"fields": ["id", "name", "email"]})
contacts_df = pd.DataFrame(contacts)
contacts_df.loc[contacts_df["email"] == False, "email"] = None
contacts_data = contacts_df[["id", "name", "email"]].values.tolist()

# handel factures from odoo db
factures = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    "account.move", "search_read",
    [[("move_type", "=", "out_invoice")]],  # Filtrer uniquement les factures de vente
    {"fields": ["id", "partner_id", "amount_total", "invoice_date"]}
)
factures_df = pd.DataFrame(factures)
factures_df["partner_name"] = factures_df["partner_id"].str[1]
factures_data = factures_df[["id", "partner_name", "amount_total", "invoice_date"]].values.tolist()



# conn = psycopg2.connect("dbname=case_chift_db user=postgres password=postgres host=localhost")
conn = psycopg2.connect("dbname=case_chift_db user=postgres password=postgres host=host.docker.internal")

cur = conn.cursor()

# Insert or update contacts
insert_or_update_contacts(cur, contacts_data)

# Delete outdated contacts
delete_old_records(cur, list(contacts_df["id"]), "contacts")

# Insert or update factures
insert_or_update_factures(cur, factures_data)

# Delete outdated factures
delete_old_records(cur, list(factures_df["id"]), "factures")


conn.commit()
cur.close()
conn.close()