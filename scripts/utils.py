import psycopg2
from psycopg2.extras import execute_values

def insert_or_update_contacts(cur, contacts_data):
    """Insert or update contacts in the database."""
    query = """
        INSERT INTO contacts (id, name, email)
        VALUES %s
        ON CONFLICT (id) DO UPDATE 
        SET name = EXCLUDED.name, email = EXCLUDED.email;
    """
    execute_values(cur, query, contacts_data)

def insert_or_update_factures(cur, factures_data):
    """Insert or update factures in the database."""
    query = """
        INSERT INTO factures (id, company, amount, invoice_date)
        VALUES %s
        ON CONFLICT (id) DO UPDATE 
        SET company = EXCLUDED.company, amount = EXCLUDED.amount, invoice_date=EXCLUDED.invoice_date;
    """
    execute_values(cur, query, factures_data)


def delete_old_records(cur, to_delete_ids, table_name):
    """Delete records that are no longer present in the latest data for a given table."""
    query = f"""
        DELETE FROM {table_name}
        WHERE id NOT IN (
            SELECT {table_name}.id FROM {table_name}
            LEFT JOIN (SELECT unnest(%s::int[]) AS id) AS latest_data
            ON {table_name}.id = latest_data.id
            WHERE latest_data.id IS NOT NULL
        );
    """
    cur.execute(query, (to_delete_ids,))

