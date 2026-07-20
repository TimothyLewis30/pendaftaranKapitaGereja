from src import app
from src.database import init_db, seed_superadmin

init_db()
seed_superadmin()
