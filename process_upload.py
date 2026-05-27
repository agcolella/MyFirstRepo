import os
import glob
import json
import configparser
import xml.etree.ElementTree as ET
from datetime import datetime
# Importiamo le funzioni core dal tuo script originale
from parse_check_cert import check_certificate, fetch_spid_certificates, process_entities

CACHE_FILE = "certificate_cache.json"

# Carica la configurazione per leggere un eventuale limite personalizzato
config = configparser.ConfigParser()
config.read("config.ini")

# PARAMETRO LIMITE: Legge 'max_scan_files' da [SETTINGS] in config.ini. 
# Se non esiste, di default imposta un limite di 10 file. Metti 0 o -1 per disattivarlo.
MAX_SCAN_FILES = config.getint("SETTINGS", "max_scan_files", fallback=10)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def extract_entity_id_from_xml(xml_path):
    """ Estratte l'entityID dall'elemento radice dell'XML dei metadati """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        entity_id = root.get('entityID')
        if not entity_id:
            for elem in root.iter():
                if elem.tag.endswith('EntityDescriptor'):
                    entity_id = elem.get('entityID')
                    break
        return entity_id.strip() if entity_id else None
    except Exception as e:
        print(f"Errore nella lettura XML di {xml_path}: {e}")
        return None

def main():
    cache = load_cache()
    uploaded_files = glob.glob("uploads/**/*.xml", recursive=True)
    
    entities_to_process = set()
    oggi = datetime.now().strftime("%Y-%m-%d")
    scanned_count = 0  # Contatore dei file che richiedono una scansione effettiva

    print(f"Trovati {len(uploaded_files)} file XML nella directory uploads.")
    print(f"Limite massimo di scansioni configurato: {MAX_SCAN_FILES} file.")

    for file_path in uploaded_files:
        # Controllo interruzione anticipata: se abbiamo raggiunto il limite massimo, ci fermiamo qui
        if MAX_SCAN_FILES > 0 and scanned_count >= MAX_SCAN_FILES:
            print(f"⚠️ Raggiunto il limite massimo di file da scansionare ({MAX_SCAN_FILES}). Interrompo l'analisi dei rimanenti file.")
            break

        entity_id = extract_entity_id_from_xml(file_path)
        if not entity_id:
            print(f"Impossibile trovare entityID nel file {file_path}. Salto.")
            continue

        # Controllo della Cache
        if entity_id in cache:
            info = cache[entity_id]
            if info.get("status") == "VALIDO" and info.get("scadenza") > oggi:
                print(f"Cache HIT per {entity_id}: Certificato valido fino al {info['scadenza']}. Controllo saltato.")
                continue

        print(f"Cache MISS o Scaduto per {entity_id}. Accodato per verifica sul Registro.")
        entities_to_process.add(entity_id)
        
        # Incrementiamo il contatore solo per i file che generano un "MISS" e richiedono attività sul registro
        scanned_count += 1

    if not entities_to_process:
        print("Nessun nuovo file da analizzare (tutti in cache o nessun file accodato prima del limite).")
        return

    # Generazione file temporaneo CSV per riutilizzare il tuo analizzatore
    temp_csv = "temp_entities_to_check.csv"
    with open(temp_csv, "w", newline="") as f:
        for ent in entities_to_process:
            f.write(f"{ent}\n")

    print(f"Avvio analisi effettiva su {len(entities_to_process)} enti (rispettando la soglia massima)...")
    process_entities(temp_csv, "Results.xlsx")

    # Aggiornamento della cache locale
    for ent in entities_to_process:
        certs, _, _ = fetch_spid_certificates(ent)
        if certs:
            with open("temp_cert.pem", "w") as f:
                f.write(f"-----BEGIN CERTIFICATE-----\n{certs[0]}\n-----END CERTIFICATE-----\n")
            res = check_certificate("temp_cert.pem")
            
            if res["Scaduto"] == "N" and res["Data Scadenza"] != "Error":
                cache[ent] = {
                    "status": "VALIDO",
                    "scadenza": res["Data Scadenza"]
                }
            else:
                cache[ent] = {
                    "status": "SCADUTO_O_INVALIDO",
                    "scadenza": res["Data Scadenza"]
                }
        else:
            cache[ent] = {
                "status": "ERRORE_REGISTRO",
                "scadenza": oggi
            }

    save_cache(cache)
    
    # Pulizia
    for temp_file in [temp_csv, "temp_cert.pem", "spid_cert.pem"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    main()
