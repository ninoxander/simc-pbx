import os
import asyncio
import threading
from flask import Flask, jsonify
from panoramisk import Manager
from supabase import create_client, Client

app = Flask(__name__)

# Asterisk + supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rrxvlnnycowdvyjbizhk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "s")
ASTERISK_HOST = os.getenv("ASTERISK_HOST", "asterisk_service")
ASTERISK_AMI_PORT = int(os.getenv("ASTERISK_AMI_PORT", 5038))
ASTERISK_AMI_USER = os.getenv("ASTERISK_AMI_USER", "ami_user")
ASTERISK_AMI_SECRET = os.getenv("ASTERISK_AMI_SECRET", "AmiSuperSecret123!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Listener AMI
async def run_ami_listener():
    manager = Manager(
        loop=asyncio.get_running_loop(),
        host=ASTERISK_HOST,
        port=ASTERISK_AMI_PORT,
        username=ASTERISK_AMI_USER,
        secret=ASTERISK_AMI_SECRET
    )

    try:
        await manager.connect()
        print("[AMI] Conectado exitosamente a Asterisk AMI")
    except Exception as e:
        print(f"[AMI Error] No se pudo conectar a Asterisk: {e}")
        return

    # Evento: Comienza una llamada (o timbrado)
    @manager.register_event('DialBegin')
    def handle_dial_begin(mngr, event):
        caller = event.get('CallerIDNum')
        dest = event.get('DestCallerIDNum')
        now_iso = datetime.now(timezone.utc).isoformat()
        print(f"[AMI Event] DialBegin: {caller} -> {dest}")

        if caller and dest:
            payload_caller = {
                'extension': str(caller),
                'status': 'IN_CALL',
                'peer_extension': str(dest),
                'call_started_at': now_iso
            }
            payload_dest = {
                'extension': str(dest),
                'status': 'IN_CALL',
                'peer_extension': str(caller),
                'call_started_at': now_iso
            }
            supabase.table('agent_status').upsert(payload_caller).execute()
            supabase.table('agent_status').upsert(payload_dest).execute()

    @manager.register_event('Hangup')
    def handle_hangup(mngr, event):
        caller = event.get('CallerIDNum')
        print(f"[AMI Event] Hangup: {caller}")

        if caller:
            supabase.table('agent_status').upsert({
                'extension': str(caller),
                'status': 'AVAILABLE',
                'peer_extension': None,
                'call_started_at': None
            }).execute()

    # Mantiene vivo el bucle asíncrono
    while True:
        await asyncio.sleep(3600)

def start_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_ami_listener())

# Rutas Flask
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "python-ai ok"}), 200

if __name__ == "__main__":
    # Arranca el worker de Asterisk en un hilo demonio en segundo plano
    ami_thread = threading.Thread(target=start_background_loop, daemon=True)
    ami_thread.start()

    print("Iniciando servicio Python AI en puerto 5000...")
    app.run(host="0.0.0.0", port=5000)