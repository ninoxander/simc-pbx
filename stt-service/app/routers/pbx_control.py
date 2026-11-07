from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import telnetlib

router = APIRouter(
    prefix="/pbx",
    tags=["Asterisk Control"]
)

class ExtensionConfig(BaseModel):
    extension: str
    secret: str

def execute_ami_command(command: str) -> str:
    """Envía comandos a Asterisk CLI a través de AMI."""
    try:
        tn = telnetlib.Telnet("asterisk_service", 5038, timeout=5)
        tn.read_until(b"Asterisk Call Manager")
        tn.write(b"Action: Login\r\nUsername: admin\r\nSecret: admin_pbx_pass\r\n\r\n")
        tn.read_until(b"Message: Authentication accepted")
        
        tn.write(f"Action: Command\r\nCommand: {command}\r\n\r\n".encode("utf-8"))
        res = tn.read_until(b"--END COMMAND--", timeout=4)
        
        tn.write(b"Action: Logoff\r\n\r\n")
        return res.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo de conexión AMI con Asterisk: {str(e)}")

@router.post("/reload")
def reload_dialplan():
    result = execute_ami_command("dialplan reload")
    return {"status": "ok", "message": "Dialplan recargado exitosamente", "output": result}

@router.post("/extensions")
def add_extension(data: ExtensionConfig):
    config_path = "/app/asterisk_configs/pjsip_custom.conf"
    
    entry = f"""
; Extensión generada desde Dashboard Web
[{data.extension}]
type=endpoint
context=from-internal
disallow=all
allow=ulaw,alaw
auth={data.extension}
aors={data.extension}

[{data.extension}]
type=auth
auth_type=userpass
password={data.secret}
username={data.extension}

[{data.extension}]
type=aor
max_contacts=1
"""
    try:
        with open(config_path, "a") as f:
            f.write(entry)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"No se pudo escribir en la configuración: {str(e)}")
        
    execute_ami_command("module reload res_pjsip.so")
    return {"status": "ok", "message": f"Extensión {data.extension} agregada y PJSIP recargado"}