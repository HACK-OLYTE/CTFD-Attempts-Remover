from flask import Blueprint, render_template, request, jsonify
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils import get_config, set_config
from CTFd.utils.user import get_current_user, get_current_team
from CTFd.models import db, Challenges, Submissions, Teams, Awards, Users
from CTFd.plugins import register_plugin_assets_directory, register_plugin_script
from datetime import datetime

# === Modèles de base de données ===

class UnblockLog(db.Model):
    __tablename__ = "attempts_unblock_logs"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship("Teams", backref="unblock_logs")
    challenge = db.relationship("Challenges", backref="unblock_logs")
    admin = db.relationship("Users", backref="unblock_logs")


class UnblockRequest(db.Model):
    __tablename__ = "attempts_remover_requests"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship("Teams", backref="attempts_remover_requests")
    challenge = db.relationship("Challenges", backref="attempts_remover_requests")


# === Plugin loader ===

def load(app):
    remover_bp = Blueprint(
        'attempts_remover',
        __name__,
        template_folder='templates',
        static_folder='assets',
        url_prefix='/plugins/ctfd-attempts-remover'
    )

    api_bp = Blueprint(
        'attempts_remover_api',
        __name__,
        url_prefix='/api/v1/attempts_remover'
    )

    # === API : Récupère les demandes en attente pour l'équipe connectée ===
    @api_bp.route("/my_requests", methods=["GET"])
    @authed_only
    def get_my_requests():
        team = get_current_team()
        requests = UnblockRequest.query.filter_by(team_id=team.id).all()
        return jsonify([{
            "challenge_id": r.challenge_id,
            "challenge_name": r.challenge.name,
            "challenge_value": r.challenge.value,
            "timestamp": r.timestamp.isoformat()
        } for r in requests])

    # === API : Récupère l'historique des déblocages acceptés pour l'équipe ===
    @api_bp.route('/my_history', methods=["GET"])
    @authed_only
    def get_my_unblock_history():
        team = get_current_team()
        if not team:
            return jsonify([])
        logs = UnblockLog.query.filter_by(team_id=team.id).order_by(UnblockLog.timestamp.desc()).all()
        return jsonify([{
            "challenge_name": l.challenge.name,
            "timestamp": l.timestamp.isoformat()
        } for l in logs])

    # === API : Créer une nouvelle demande de déblocage pour un challenge ===
    @api_bp.route('/request_support', methods=["POST"])
    @authed_only
    def request_support():
        data = request.get_json()
        challenge_id = data.get("challenge_id")
        team = get_current_team()

        if not team or not challenge_id:
            return jsonify(success=False, error="Équipe ou challenge manquant"), 400

        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return jsonify(success=False, error="Challenge introuvable"), 404

        existing = UnblockRequest.query.filter_by(team_id=team.id, challenge_id=challenge.id).first()
        if existing:
            return jsonify(success=False, error="Une demande a déjà été envoyée."), 400

        req = UnblockRequest(team_id=team.id, challenge_id=challenge.id)
        db.session.add(req)
        db.session.commit()
        return jsonify(success=True)

    # === API : Retourne les challenges actuellement bloqués ===
    @api_bp.route('/blocked', methods=["GET"])
    @authed_only
    def user_blocked_challenges():
        team = get_current_team()
        user = get_current_user()
        if not team and not user:
            return jsonify([])

        is_team_mode = team is not None
        id_used = team.id if is_team_mode else user.id
        challenges = Challenges.query.filter(Challenges.max_attempts > 0).all()

        blocked = []
        for chal in challenges:
            query = Submissions.query.filter_by(challenge_id=chal.id, type="incorrect")
            query = query.filter_by(team_id=id_used) if is_team_mode else query.filter_by(user_id=id_used)
            count = query.count()
            if count >= chal.max_attempts:
                blocked.append({
                    "challenge_id": chal.id,
                    "challenge_name": chal.name,
                    "value": chal.value,
                    "fail_count": count,
                    "max_attempts": chal.max_attempts
                })
        return jsonify(blocked)

    # === API : Retourne la configuration actuelle du malus ===
    @api_bp.route('/config', methods=["GET"])
    @authed_only
    def get_config_route():
        return jsonify({
            "mode": get_config("attempts_remover:mode") or "fixed",
            "fixed_cost": int(get_config("attempts_remover:fixed_cost") or 100),
            "percent_cost": int(get_config("attempts_remover:percent_cost") or 10)
        })

    # === API : Permet à un admin de modifier la configuration ===
    @api_bp.route('/config', methods=["POST"])
    @admins_only
    def set_config_route():
        data = request.get_json()
        set_config("attempts_remover:mode", data.get("mode"))
        set_config("attempts_remover:fixed_cost", data.get("fixed_cost"))
        set_config("attempts_remover:percent_cost", data.get("percent_cost"))
        return jsonify(success=True)

    # === API : Retourne les logs de déblocage (admin) ===
    @api_bp.route('/unblock_logs', methods=["GET"])
    @admins_only
    def get_unblock_logs():
        logs = UnblockLog.query.order_by(UnblockLog.timestamp.desc()).limit(50).all()
        return jsonify([{
            "timestamp": l.timestamp.isoformat(),
            "admin_name": l.admin.name,
            "team_name": l.team.name,
            "challenge_name": l.challenge.name
        } for l in logs])

    # === API : Liste des blocages actuels toutes équipes confondues (admin) ===
    @api_bp.route('/admin_blocked', methods=["GET"])
    @admins_only
    def get_all_blocked_teams():
        challenges = Challenges.query.filter(Challenges.max_attempts > 0).all()
        teams = Teams.query.all()

        all_blocks = []
        for team in teams:
            for chal in challenges:
                fail_count = Submissions.query.filter_by(
                    team_id=team.id,
                    challenge_id=chal.id,
                    type='incorrect'
                ).count()

                if fail_count >= chal.max_attempts:
                    already_requested = UnblockRequest.query.filter_by(
                        team_id=team.id,
                        challenge_id=chal.id
                    ).first()

                    all_blocks.append({
                        "team_id": team.id,
                        "team_name": team.name,
                        "challenge_id": chal.id,
                        "challenge_name": chal.name,
                        "fail_count": fail_count,
                        "max_attempts": chal.max_attempts,
                        "challenge_value": chal.value,
                        "value": chal.value,
                        "requested": bool(already_requested)
                    })
        return jsonify(all_blocks)

    # === API : Action d’un admin pour débloquer une équipe sur un challenge ===
    @api_bp.route('/admin_unblock', methods=["POST"])
    @admins_only
    def force_unblock_team():
        data = request.get_json()
        team_id = data.get("team_id")
        challenge_id = data.get("challenge_id")

        if not team_id or not challenge_id:
            return jsonify(success=False, error="Paramètres manquants"), 400

        team = Teams.query.filter_by(id=team_id).first()
        challenge = Challenges.query.filter_by(id=challenge_id).first()

        if not team or not challenge:
            return jsonify(success=False, error="Équipe ou challenge introuvable"), 404

        fails = Submissions.query.filter_by(
            challenge_id=challenge.id,
            team_id=team.id,
            type="incorrect"
        ).all()

        if not fails:
            return jsonify(success=False, error="Aucune tentative incorrecte à supprimer"), 400

        for f in fails:
            db.session.delete(f)

        mode = get_config("attempts_remover:mode") or "fixed"
        fixed_cost = int(get_config("attempts_remover:fixed_cost") or 100)
        percent_cost = int(get_config("attempts_remover:percent_cost") or 10)

        if mode == "fixed":
            cost = fixed_cost
        else:
            cost = int(abs(challenge.value) * percent_cost / 100)

        user = Users.query.filter_by(team_id=team.id).first()
        if not user:
            return jsonify(success=False, error="Aucun membre trouvé pour cette équipe"), 400

        award = Awards(
            team_id=team.id,
            user_id=user.id,
            name=f"Déblocage challenge - {challenge.name}",
            value=-cost,
            category="Malus",
            icon="shield"
        )
        db.session.add(award)

        admin = get_current_user()
        if admin:
            log = UnblockLog(
                team_id=team.id,
                challenge_id=challenge.id,
                admin_id=admin.id,
                timestamp=datetime.utcnow()
            )
            db.session.add(log)

        existing_request = UnblockRequest.query.filter_by(
            team_id=team.id,
            challenge_id=challenge.id
        ).first()
        if existing_request:
            db.session.delete(existing_request)

        db.session.commit()

        return jsonify(success=True, removed=len(fails), cost=cost, challenge=challenge.name)


    # === Pages HTML ===

    @remover_bp.route('/unblock')
    @authed_only
    def unblock_page():
        return render_template('ctfd_attempts_remover_unblock.html')

    @remover_bp.route('/admin')
    @admins_only
    def admin_page():
        return render_template('ctfd_attempts_remover_admin.html')

    # === Initialisation plugin et BDD ===

    with app.app_context():
        #db.engine.execute("DROP TABLE IF EXISTS attempts_remover_requests")
        #db.engine.execute("DROP TABLE IF EXISTS attempts_unblock_logs")
        db.session.commit()
        db.create_all()

    app.register_blueprint(remover_bp)
    app.register_blueprint(api_bp)
    register_plugin_assets_directory(app, base_path='/plugins/ctfd-attempts-remover/assets')
    register_plugin_script('/plugins/ctfd-attempts-remover/assets/settingsremover.js')
