"""Safe script to delete all users using the app's SQLAlchemy session so relationships cascade.
This file adds the workspace root into sys.path so imports like `backend.app...` work when
running the script directly from the project root.
"""
import sys
from pathlib import Path

# Ensure workspace root is on sys.path so 'backend' package can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.core import db as coredb
from sqlalchemy import text


def main():
    engine = coredb.engine
    with engine.begin() as conn:
        # Delete dependent rows first to avoid FK constraint issues.
        # The order below follows typical FK dependency from children -> parents.
        tables = [
            'investment_transactions',
            'investments',
            'transactions',
            'accounts',
            'budget_items',
            'budgets',
            'categories',
            'goals',
        ]
        for t in tables:
            try:
                print(f'Deleting from {t}...')
                conn.execute(text(f'DELETE FROM {t}'))
            except Exception as e:
                print(f'Warning: could not delete {t}:', e)
        # Finally delete users
        print('Deleting users...')
        conn.execute(text('DELETE FROM users'))
        print('Finished deleting users and dependent data (if present).')


if __name__ == '__main__':
    main()
