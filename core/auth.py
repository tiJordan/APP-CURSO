from ldap3 import Server, Connection, NTLM, core
from settings import AD_SERVER, AD_DOMAIN, AD_BASEDN

def autenticar_ad(usuario, senha):
    usuario_completo = f"{AD_DOMAIN}\\{usuario}"
    server = Server(AD_SERVER)
    try:
        conn = Connection(server, user=usuario_completo, password=senha, authentication=NTLM, auto_bind=True)
        return True
    except core.exceptions.LDAPBindError:
        return False


def is_user_in_group(usuario: str, senha: str, group_cn: str) -> bool:
     """
     Retorna True se 'usuario' for membro do grupo CN=group_cn,
     usando as próprias credenciais do usuário para o bind.
     """
     server = Server(AD_SERVER)
     user_upn = f"{AD_DOMAIN}\\{usuario}"
     try:
         # 1) Bind com as credenciais do próprio usuário
         conn = Connection(server,
                           user=user_upn,
                           password=senha,
                           authentication=NTLM,
                           auto_bind=True)
 
         # 2) Busca DN do usuário
         conn.search(
             AD_BASEDN,
             f"(sAMAccountName={usuario})",
             attributes=["distinguishedName"]
         )
         if not conn.entries:
             return False
         user_dn = conn.entries[0].distinguishedName.value
 
         # 3) Verifica membership do grupo
         conn.search(
             AD_BASEDN,
             f"(&(objectClass=group)(cn={group_cn})(member={user_dn}))",
             attributes=["cn"]
         )
         return bool(conn.entries)
     except core.exceptions.LDAPBindError:
         # Falha no bind com o usuário: senha inválida?
         return False
     except Exception:
         return False