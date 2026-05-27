import os
import glob
import json
import xml.etree.ElementTree as ET
from datetime import datetime
# Importiamo le funzioni core dal tuo script originale
from parse_check_cert import check_certificate, fetch_spid_certificates, process_entities

CACHE_FILE = "certificate_cache.json"

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
    """ Estrae l'entityID dall'elemento radice dell'XML dei metadati """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Gestione dei namespace comuni SAML/Metadata
        entity_id = root.get('entityID')
        if not entity_id:
            # Tenta la ricerca con i namespace
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

    print(f"Trovati {len(uploaded_files)} file XML nella directory uploads.")

    for file_path in uploaded_files:
        entity_id = extract_entity_id_from_xml(file_path)
        if not entity_id:
            print(f"Impossibile trovare entityID nel file {file_path}. Salto.")
            continue

        # Controllo della Cache
        if entity_id in cache:
            info = cache[entity_id]
            # Se il certificato era valido e la data di scadenza è successiva a oggi, usiamo la cache
            if info.get("status") == "VALIDO" and info.get("scadenza") > oggi:
                print(f"Cache HIT per {entity_id}: Certificato valido fino al {info['scadenza']}. Controllo saltato.")
                continue

        print(f"Cache MISS o Scaduto per {entity_id}. Accodato per verifica sul Registro.")
        entities_to_process.add(entity_id)

    if not entities_to_process:
        print("Tutti i file caricati contengono certificati ancora in cache e validi. Nessuna operazione necessaria.")
        return

    # Genera un file temporaneo csv_file per riutilizzare la tua funzione process_entities
    temp_csv = "temp_entities_to_check.csv"
    with open(temp_csv, "w", newline="") as f:
        for ent in entities_to_process:
            f.write(f"{ent}\n")

    print(f"Avvio analisi di {len(entities_to_process)} enti tramite parse_check_cert.py...")
    # Esegue il tuo processore originale che genera Results.xlsx
    process_entities(temp_csv, "Results.xlsx")

    # Aggiorna la cache sulla base delle nuove verifiche effettuate
    for ent in entities_to_process:
        certs, _, _ = fetch_spid_certificates(ent)
        if certs:
            # Per semplicità verifichiamo il primo certificato restituito (o adegua se cicli)
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
    
    # Pulizia file temporanei
    for temp_file in [temp_csv, "temp_cert.pem", "spid_cert.pem"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    main()
