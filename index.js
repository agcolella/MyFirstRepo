const fs = require('fs');
const https = require('https');

const REPO_OWNER = 'agcolella';
const REPO_NAME = 'MyFirstRepo';

// Helper per effettuare richieste HTTP asincrone (Promises) verso le API di GitHub
function githubFetch(path) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.github.com',
            path: path,
            method: 'GET',
            headers: {
                'User-Agent': 'NodeJS-Metadata-App',
                'Authorization': process.env.GITHUB_TOKEN ? `token ${process.env.GITHUB_TOKEN}` : ''
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                if (res.statusCode !== 200) {
                    reject(new Error(`GitHub API Error: ${res.statusCode} su ${path}`));
                } else {
                    resolve(JSON.parse(data));
                }
            });
        });
        req.on('error', (e) => reject(e));
        req.end();
    });
}

// Funzione per pulire il titolo della PR ed estrarre il nome dell'Ente pulito
function estraiNomeEnte(title) {
    if (!title) return "Ente non specificato";
    
    // Rimuove emoji, tag quadre tipo [20260526-1331], prefissi "Revisione XML" o "Update"
    let pulito = title
        .replace(/[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDC00-\uDFFF]/g, '') // Rimuove Emoji
        .replace(/\[.*?\]/g, '') // Rimuove tutto ciò che è dentro le parentesi quadre []
        .replace(/(Revisione XML|Update|Modifica Metadati|Metadata)/gi, '') // Rimuove parole chiave del workflow
        .trim();

    return pulito || "Ente Revisionato";
}

async function main() {
    try {
        console.log("1. Recupero l'elenco di tutte le Pull Request...");
        const prList = await githubFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/pulls?state=all&per_page=100`);
        
        const finalDataset = [];

        console.log(`2. Analizzo i file modificati per ciascuna delle ${prList.length} PR trovate...`);
        for (const pr of prList) {
            try {
                // Recupera la lista dei file modificati in questa specifica PR
                const files = await githubFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/pulls/${pr.number}/files`);
                
                // Cerchiamo il primo file XML valido modificato nella PR
                const xmlFile = files.find(f => f.filename && f.filename.toLowerCase().endsWith('.xml'));

                // Se la PR non tocca file XML, usiamo i fallback basati sulla PR stessa
                const filename = xmlFile ? xmlFile.filename.split('/').pop() : `${pr.head?.ref || 'patch'}.xml`;
                
                // L'URL dei metadati: se c'è l'XML usiamo il link al file grezzo (raw) o al repository, 
                // altrimenti manteniamo il fallback dell'URL della PR
                const urlMetadati = xmlFile ? xmlFile.raw_url : pr.html_url;

                // Pulizia dell'ente dal titolo
                const nomeEnte = estraiNomeEnte(pr.title);

                finalDataset.push({
                    ente: nomeEnte,
                    url: urlMetadati,
                    filename: filename,
                    pr_number: pr.number.toString(),
                    pr_date: pr.created_at ? pr.created_at.split('T')[0] : "",
                    pr_status: pr.merged_at ? 'merged' : pr.state
                });

            } catch (fileError) {
                console.error(`Errore durante l'analisi dei file della PR #${pr.number}:`, fileError.message);
                // Fallback sicuro se fallisce la chiamata sui singoli file
                finalDataset.push({
                    ente: estraiNomeEnte(pr.title),
                    url: pr.html_url,
                    filename: `${pr.head?.ref || 'unknown'}.xml`,
                    pr_number: pr.number.toString(),
                    pr_date: pr.created_at ? pr.created_at.split('T')[0] : "",
                    pr_status: pr.merged_at ? 'merged' : pr.state
                });
            }
        }

        // Scrittura finale del file con la struttura corretta richiesta
        fs.writeFileSync('data.json', JSON.stringify(finalDataset, null, 2));
        console.log(` Done! File data.json generato con successo con ${finalDataset.length} record.`);

    } catch (error) {
        console.error("Errore critico nel processo principale:", error);
        process.exit(1);
    }
}

main();
