from pathlib import Path

c = get_config()

c.PasswordIdentityProvider.hashed_password = Path("/run/secrets/jupyter_shared_hash").read_text().strip()
c.PasswordIdentityProvider.password_required = True
c.PasswordIdentityProvider.allow_password_change = False

c.ServerApp.token = ""
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = "/workspace"
c.ServerApp.allow_remote_access = True
c.ServerApp.allow_root = False
c.ServerApp.allow_unauthenticated_access = False
