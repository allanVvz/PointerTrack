# ble_hm10_reader.py

import asyncio
from bleak import BleakScanner, BleakClient
from insert_local import insert_local_from_json, close_inserter


# UUIDs do HM‑10 (BLE) padrão para UART emblema: FFE0/FFE1
HM10_SERVICE_UUID      = "0000ffe0-0000-1000-8000-00805f9b34fb"
HM10_CHAR_RX_UUID      = "0000ffe1-0000-1000-8000-00805f9b34fb"

DEVICE_NAME = "CORE"
SCAN_TIMEOUT = 5.0  # segundos
buffer             = ""

async def notification_handler(sender, data: bytearray):
    global buffer
    chunk = data.decode('ascii', errors='ignore')
    buffer += chunk
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            insert_local_from_json(line)

async def run():

    print(f"Escaneando por '{DEVICE_NAME}' ({SCAN_TIMEOUT}s)…")
    devices = await BleakScanner.discover(timeout=SCAN_TIMEOUT)
    target = next((d for d in devices if d.name == DEVICE_NAME), None)
    if not target:
        print("❌ Dispositivo não encontrado.")
        return

    print(f"➜ Encontrado {target.name} [{target.address}]")
    async with BleakClient(target.address) as client:
        
        # Bleak v0.20+: is_connected é propriedade
        if not client.is_connected:
            print("❌ Falha ao conectar.")
            return
        print("✅ Conectado!")
       
        # **Liste serviços e characteristics** para verificar UUIDs
        svcs = await client.get_services()
        print("Serviços encontrados:")
        for svc in svcs:
            print(f" • Service: {svc.uuid}")
            for ch in svc.characteristics:
                props = ",".join(ch.properties)
                print(f"   └ Char: {ch.uuid} ({props})")

        # Aguarde um pouco antes de assinar
        await asyncio.sleep(1)

        # Inicie notificações na característica FFE1
        print(f"\nInscrevendo em {HM10_CHAR_RX_UUID}…")
        await client.start_notify(HM10_CHAR_RX_UUID, notification_handler)

        print("🔄 Lendo dados BLE (CTRL+C para sair)…\n")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        close_inserter()
        print("\n❎ Encerrado pelo usuário.")
