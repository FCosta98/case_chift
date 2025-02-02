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
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# conn = psycopg2.connect("dbname=case_chift_db user=postgres password=postgres host=localhost") # to use with python3 script_odoo.py
# conn = psycopg2.connect("dbname=case_chift_db user=postgres password=postgres host=host.docker.internal") # to use for docker locally
conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME) # to use for the deployed DB on supabase
cur = conn.cursor()


# Authentification odoo
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

if uid:
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
else:
    raise Exception("Échec de l'authentification à Odoo")

# handel contacts from odoo db
contacts = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search_read", [[]], {"fields": ["id", "name", "email"]})
contacts_df = pd.DataFrame(contacts)
if not contacts_df.empty:
    contacts_df.loc[contacts_df["email"] == False, "email"] = None
    contacts_data = contacts_df[["id", "name", "email"]].values.tolist()
    insert_or_update_contacts(cur, contacts_data)
    delete_old_records(cur, list(contacts_df["id"]), "contacts")
else:
    delete_old_records(cur, list(), "contacts")

# handel factures from odoo db
factures = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    "account.move", "search_read",
    [[("move_type", "=", "out_invoice")]],  # Filtrer uniquement les factures de vente
    {"fields": ["id", "partner_id", "amount_total", "invoice_date"]}
)
factures_df = pd.DataFrame(factures)
if not factures_df.empty:
    factures_df["partner_name"] = factures_df["partner_id"].str[1]
    factures_data = factures_df[["id", "partner_name", "amount_total", "invoice_date"]].values.tolist()
    insert_or_update_factures(cur, factures_data)
    delete_old_records(cur, list(factures_df["id"]), "factures")
else:
    delete_old_records(cur, list(), "factures")


conn.commit()
cur.close()
conn.close()