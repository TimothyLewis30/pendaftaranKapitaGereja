from src import app
from src.database import init_db, seed_superadmin

if __name__ == "__main__":
    init_db()
    seed_superadmin()
    app.run(host="0.0.0.0", port=8080, debug=True)
