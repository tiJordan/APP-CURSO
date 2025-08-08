# core/audit.py
from datetime import datetime
from core.db import SessionLocal, AuditEvent
from sqlalchemy import and_

class AuditLogger:
    def __init__(self):
        # cada instância abre sua própria sessão
        self.db = SessionLocal()

    def record_login(self, username: str):
        evt = AuditEvent(user=username, event="login", timestamp=datetime.now())
        self.db.add(evt)
        self.db.commit()

    def record_logout(self, username: str):
        evt = AuditEvent(user=username, event="logout", timestamp=datetime.now())
        self.db.add(evt)
        self.db.commit()

    def get_sessions(self, user: str = None, start: datetime = None, end: datetime = None):
        """
        Monta pares login–logout filtrados por usuário e período.
        """
        # 1) Buscar todos os eventos válidos no intervalo
        q = self.db.query(AuditEvent)
        if user:
            q = q.filter(AuditEvent.user == user)
        if start:
            q = q.filter(AuditEvent.timestamp >= start)
        if end:
            q = q.filter(AuditEvent.timestamp <= end)
        events = q.order_by(AuditEvent.timestamp).all()

        # 2) Emparelhar login + logout
        sessions = []
        stack = {}
        for e in events:
            if e.event == "login":
                stack[e.user] = e.timestamp
            elif e.event == "logout" and e.user in stack:
                login_ts = stack.pop(e.user)
                sessions.append({
                    "user": e.user,
                    "login_time": login_ts,
                    "logout_time": e.timestamp,
                    "duration": e.timestamp - login_ts
                })
        return sessions

    def get_active_sessions(self):
        """
        Sessões com login sem logout correspondente.
        """
        # pegamos todos logins e logouts
        logins  = self.db.query(AuditEvent).filter(AuditEvent.event == "login").all()
        logouts = self.db.query(AuditEvent).filter(AuditEvent.event == "logout").all()

        # mapa usuário → lista de logout timestamps
        logout_map = {}
        for e in logouts:
            logout_map.setdefault(e.user, []).append(e.timestamp)

        active = []
        now = datetime.now()
        for l in logins:
            # se não existe logout posterior ao login, consideramos ativo
            user = l.user
            # todos os logouts dessa pessoa após o login
            outs = [t for t in logout_map.get(user, []) if t > l.timestamp]
            if not outs:
                active.append({
                    "user": user,
                    "login_time": l.timestamp,
                    "logout_time": None,
                    "duration": now - l.timestamp
                })
        # opcional: dedup final para o caso de múltiplos logins sem logout
        seen = set()
        uniq = []
        for s in active:
            if s["user"] not in seen:
                uniq.append(s); seen.add(s["user"])
        return uniq
