import sys
import traceback

try:
    print("Attempting to import app...")
    from app import app, db
    print("Import successful.")
    
    print("Attempting to initialize DB...")
    with app.app_context():
        db.create_all()
    print("DB init successful.")
    
    print("Starting app...")
    app.run(debug=True, use_reloader=False)
except Exception:
    print("Exception occurred:")
    traceback.print_exc()
except SystemExit as e:
    print(f"SystemExit: {e}")
