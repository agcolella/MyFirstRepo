const fs = require('fs');
const https = require('https');

// Configurazione dei dettagli del repository
const REPO_OWNER = 'agcolella';
const REPO_NAME = 'MyFirstRepo';

// Configura le opzioni per la chiamata HTTP alle API di GitHub
const options = {
    hostname: 'api.github.com',
    path: `/repos/${REPO_OWNER}/${REPO_NAME}/pulls?state=all&per_page=100`,
    method: 'GET',
    headers: {
        'User-Agent': 'NodeJS-Metadata-App',
        // Utilizza il token passato automaticamente dalle GitHub Actions per evitare limiti di chiamate
        'Authorization': process.env.GITHUB_TOKEN ? `token ${process.env.GITHUB_TOKEN}` : ''
    }
};

console.log("Recupero delle Pull Request da GitHub in corso...");

const req = https.request(options, (res) => {
    let data = '';

    res.on('data', (chunk) => {
        data += chunk;
    });

    res.on('end', () => {
        if (res.statusCode !== 200) {
            console.error(`Errore API GitHub: Stato ${res.statusCode}`);
            console.error(data);
            process.exit(1);
        }

        try {
            const prList = JSON.parse(data);
            console.log(`Trovate ${prList.length} Pull Request. Elaborazione dati...`);

            // Mappatura e trasformazione dei dati per la dashboard index.html
            // NOTA: Qui estraiamo le info delle PR. Se hai un elenco predefinito di enti,
            // puoi fare un "join" o una mappatura basandoti sul titolo o sui file della PR.
            const dataset = prList.map(pr => {
                // Esempio di estrazione metadati basato sul titolo o dati standard della PR
                return {
                    ente: pr.title || "Ente non specificato",
                    url: pr.html_url, // Link generico se non c'è nei metadati della PR
                    filename: pr.head?.ref || "unknown_file.xml",
                    pr_number: pr.number.toString(),
                    pr_date: pr.created_at.split('T')[0], // Estrae solo la data YYYY-MM-DD
                    pr_status: pr.merged_at ? 'merged' : pr.state // Gestisce open, closed o merged
                };
            });

            // Scrittura del file richiesto dalla dashboard
            fs.writeFileSync('data.json', JSON.stringify(dataset, null, 2));
            console.log("File data.json generato con successo!");

        } catch (error) {
            console.error("Errore nel parsing del JSON di risposta:", error);
            process.exit(1);
        }
    });
});

req.on('error', (e) => {
    console.error(`Errore durante la richiesta: ${e.message}`);
    process.exit(1);
});

req.end();