from flask import render_template, request, redirect, url_for, session, jsonify
from app import app, db
from app.models import Pergunta

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/criar_pergunta", methods=["GET", "POST"])
def criar_pergunta():
    if request.method == "POST":
        try:
            texto = request.form["texto"]
            resposta_correta = request.form["resposta_correta"]
            
            if not texto or not resposta_correta:
                raise ValueError("Texto da pergunta ou resposta incorreta não preenchidos corretamente.")

            pergunta = Pergunta(texto=texto, resposta_correta=resposta_correta)
            db.session.add(pergunta)
            db.session.commit()

            return redirect(url_for("index"))
        except Exception as e:
            return f"Erro: {str(e)}", 500

    return render_template("criar_pergunta.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if 'pergunta_atual' not in session:
        session['pergunta_atual'] = 0

    perguntas = Pergunta.query.all()

    if session['pergunta_atual'] >= len(perguntas):
        return redirect(url_for('resultado'))

    pergunta_atual = perguntas[session['pergunta_atual']]

    if request.method == "POST":
        resposta = request.form["resposta"]
        respostas = session.get("respostas", [])
        respostas.append({"pergunta_id": pergunta_atual.id, "resposta": resposta})
        session["respostas"] = respostas

        #avança para a proxima pergunta
        session['pergunta_atual'] += 1
        return redirect(url_for('quiz'))

    return render_template("quiz.html", pergunta=pergunta_atual)

@app.route("/resultado", methods=["GET", "POST"])
def resultado():
    respostas = session.get("respostas", [])
    
    if not respostas:
        return jsonify({"status": "error", "message": "Nenhuma resposta foi fornecida."}), 400

    pontuacao = 0
    for resposta in respostas:
        pergunta = Pergunta.query.get(resposta["pergunta_id"])
        if pergunta.resposta_correta == resposta["resposta"]:
            pontuacao += 1

    total_perguntas = len(respostas)
    percentual = (pontuacao / total_perguntas) * 100

    if percentual >= 50:
        resultado = "Você foi bem!"
        status = "success"
    else:
        resultado = "Tente novamente!"
        status = "error"

    return render_template("resultado.html", 
                           pontuacao=pontuacao, 
                           total_perguntas=total_perguntas, 
                           resultado=resultado, 
                           percentual=percentual)


@app.route("/reset_perguntas", methods=["POST"])
def reset_perguntas():
    try:
        perguntas = Pergunta.query.all()
        
        if request.method == "POST":        
            if not perguntas:
                abort(404, description="Nenhuma pergunta encontrada para deletar.")
            for pergunta in perguntas:
                db.session.delete(pergunta)
        
            db.session.commit()
        
            return jsonify({"message": "Todas as perguntas foram deletadas com sucesso!"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
