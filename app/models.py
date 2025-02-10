from app import db

class Pergunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(100), nullable=False)
    resposta_correta = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Pergunta {self.texto}>"
