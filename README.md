# 📂 Sistema di Gestione Registro XML

Questo repository automatizza il consolidamento, la validazione e il backup (tagging) dei file XML per il registro. Include una dashboard web per la ricerca avanzata e il ripristino rapido dei dati.

## 🚀 Link Rapidi
*   **Console di Gestione (Dashboard):** [https://agcolella.github.io/MyFirstRepo/](https://agcolella.github.io/MyFirstRepo/)
*   **Carica nuovi file:** [Clicca qui per andare alla cartella uploads](https://github.com/agcolella/MyFirstRepo/upload/main/uploads)

---

## 🛠 Come Funziona (Workflow Operativo)

Il sistema segue un flusso a "catena" per garantire l'integrità dei dati:

1.  **Caricamento:** L'utente carica file `.xml` o `.zip` nella cartella `uploads/`.
2.  **Consolidamento Automatico:** GitHub Actions estrae i file, li sposta in `registro_files/` e svuota la cartella di upload.
3.  **Revisione:** Viene creata automaticamente una **Pull Request (PR)**. L'utente deve controllarla e cliccare su **"Merge pull request"**.
4.  **Auto-Tagging:** Al merge, il sistema crea un **Tag immutabile** (es. `v-20260515-1030`) che funge da backup storico.
5.  **Dashboard:** La dashboard si aggiorna mostrando i nuovi contenuti e permettendo la ricerca per organizzazione (es. Comune).

---

## 🖥 Dashboard & Ricerca Avanzata

La dashboard (GitHub Pages) permette di:
*   **Cercare file** non solo per nome, ma anche per contenuto (es. cercando il nome dell'Ente o l'URL nel tag `<md:Organization>`).
*   **Visualizzare l'XML** direttamente in un popup cliccando sul nome del file.
*   **Effettuare Rollback:** Selezionando un Tag, il sistema genera il comando `git checkout` esatto per ripristinare un singolo file a una versione precedente.

---

## 🚨 Procedure di Emergenza (Rollback)

Se un file caricato è errato e vuoi ripristinare la versione di ieri:

1.  Apri la [Dashboard](https://agcolella.github.io/MyFirstRepo/).
2.  Cerca il file desiderato nella barra di ricerca.
3.  Dal menu a tendina, seleziona il **Tag** temporale desiderato.
4.  Clicca su **"Copia Rollback"**.
5.  Incolla il comando nel tuo terminale e premi Invio.
6.  Esegui il commit e il push:
    ```bash
    git add registro_files/
    git commit -m "Ripristino versione storica file"
    git push origin main
    ```

---

## 📁 Struttura del Repository

*   `.github/workflows/`: Contiene gli script di automazione (`consolidamento_xml.yml` e `auto_tagger.yml`).
*   `uploads/`: Cartella di transito per i nuovi caricamenti.
*   `registro_files/`: Il registro ufficiale dei file consolidati.
*   `index.html`: Il codice della dashboard web.

---

## ⚠️ Note per i Collaboratori
*   Non modificare direttamente i file in `registro_files/` se non per emergenze. Usa sempre la cartella `uploads/`.
*   Assicurarsi che gli XML siano ben formati per evitare il fallimento dei workflow.
*   Il sistema di ricerca nella dashboard è *case-insensitive* (non distingue tra maiuscole e minuscole).

