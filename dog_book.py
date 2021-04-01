from app import app, db
from app.models import User, Dog, Slot, Blast, BlastConfig

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Dog': Dog, 'Slot': Slot, 'Blast': Blast, 'BlastConfig': BlastConfig}