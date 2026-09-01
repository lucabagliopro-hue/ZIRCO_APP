import datetime
import sqlite3

class ZircoEngine:
    def __init__(self):
        self.system_name = "ZIRCO"
        self.status = "ONLINE"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect("zirco.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercice TEXT,
                charge_reps TEXT,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_status(self):
        return {
            "system": self.system_name,
            "status": self.status,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }

    def process_command(self, user_input: str) -> str:
        cmd = user_input.strip().lower()
        if "statut" in cmd or "status" in cmd:
            return "Tous les systèmes sont opérationnels, Monsieur. Prêt pour les instructions."
        elif "brief" in cmd:
            return "Briefing actif : Focus sur les objectifs du jour (Discipline, Avancement CNAM, Projets Maker)."
        else:
            return f"Commande '{user_input}' enregistrée, Monsieur."

    def get_scheduled_brief(self, brief_type: str) -> str:
        briefs = {
            "08h00": "Briefing Métallurgie : Veille alliages, R&D et procédés d'élaboration.",
            "12h00": "Briefing Recrutement : Opportunités Ingénierie/Méthodes (Alsace / Suisse).",
            "14h00": "Briefing Physique Quantique & EPR : Veille scientifique et atomique.",
            "20h00": "Bilan Technique : Synthèse labo, usinage, projets Maker et avancement CNAM."
        }
        return briefs.get(brief_type, "Aucun brief programmé pour cet horaire.")

    def log_workout(self, exercice: str, charge_reps: str, notes: str):
        conn = sqlite3.connect("zirco.db")
        cursor = conn.cursor()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT INTO workouts (date, exercice, charge_reps, notes) VALUES (?, ?, ?, ?)",
                       (date_str, exercice, charge_reps, notes))
        conn.commit()
        conn.close()
        return "Séance enregistrée avec succès, Monsieur."

    def get_workouts(self):
        conn = sqlite3.connect("zirco.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, exercice, charge_reps, notes FROM workouts ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        return rows