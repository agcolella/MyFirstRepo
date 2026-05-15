# 📂 Registro Nazionale XML Metadata

Benvenuto nel sistema automatizzato di gestione e consolidamento dei metadata XML. Questo repository utilizza GitHub Actions per processare i caricamenti e GitHub Pages per fornire una console di controllo avanzata.

## 🚀 Collegamenti Rapidi
*   **🌐 Console Dashboard (Time Machine):** [https://agcolella.github.io/MyFirstRepo/](https://agcolella.github.io/MyFirstRepo/)
*   **📥 Carica Nuovi File:** [Vai alla cartella Uploads](https://github.com/agcolella/MyFirstRepo/upload/main/uploads)

---

## 🛠️ Flusso di Lavoro (Workflow)

Il sistema è progettato per essere gestito interamente tramite interfaccia web:

1.  **Caricamento:** Trascina i tuoi file XML (o file ZIP contenenti XML) nella cartella `uploads/`.
2.  **Consolidamento:** Una procedura automatica rileverà i file, li rinomerà/validerà e li sposterà in `registro_files/`.
3.  **Approvazione:** Il sistema aprirà una **Pull Request (PR)**. Entra nella PR, verifica l'elenco dei file nel report e clicca su **Merge**.
4.  **Archiviazione:** Al merge, i file diventano ufficiali e viene creato un **Tag di Backup** (punto di ripristino) immutabile.

---

## 🖥️ La Dashboard (Time Machine)

La Dashboard non è solo un elenco di file, ma uno strumento di analisi potente:

*   **Ricerca Full-Text:** Puoi cercare un Ente per nome (es: "Comune di Senerchia") o per URL. Lo script analizzerà il contenuto dei tag `<md:Organization>` all'interno degli XML.
*   **Filtro Temporale:** Usa il calendario per selezionare una data specifica. La Dashboard ti mostrerà solo i file presenti nel registro in quel preciso giorno.
*   **Anteprima Immediata:** Clicca sul nome di un file per visualizzarne il codice XML in un popup senza doverlo scaricare.

---

## ⏪ Guida al Rollback (Ripristino Versioni Precedenti)

In caso di errori nei caricamenti, è possibile ripristinare una versione specifica di un file utilizzando i Tag generati automaticamente.

### 1. Configurazione Iniziale (Solo la prima volta)
Per eseguire i ripristini sul tuo PC, Git deve essere configurato:
```bash
git clone [https://github.com/agcolella/MyFirstRepo.git](https://github.com/agcolella/MyFirstRepo.git)
cd MyFirstRepo
