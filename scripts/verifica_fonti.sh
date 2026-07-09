#!/usr/bin/env bash
# Verifica che gli endpoint delle fonti citate nei cataloghi e nelle eval rispondano.
# Esiti: OK (2xx/3xx), ANTI-BOT (401/403/429: il sito vive ma blocca i fetch automatici,
# come documentato nei cataloghi), ERRORE (timeout, DNS, 404, 5xx).
# Uso: scripts/verifica_fonti.sh  — exit code 1 se almeno una fonte è in ERRORE.
#
# Nota su curl -k: questo script scarta il corpo (-o /dev/null) e legge solo lo
# status code HTTP per un controllo di reachability, non recupera né si fida di
# alcun contenuto. -k è qui perché alcuni domini della PA italiana (tra cui
# normattiva.it e italgiure.giustizia.it) usano catene di CA che il bundle
# ca-certificates di alcuni ambienti (runner CI inclusi, e alcune postazioni
# locali) non riconosce: senza -k la verifica del certificato fallirebbe anche
# quando il sito è raggiungibile e legittimo. Non riusare -k per fetch che
# leggono o citano il contenuto della risposta: qui serve solo a non confondere
# un gap del trust store locale con un sito realmente irraggiungibile.
set -uo pipefail

URLS=(
  "https://www.normattiva.it/"
  "https://www.normattiva.it/legislazioneRegionale"
  "https://eur-lex.europa.eu/"
  "https://www.gazzettaufficiale.it/"
  "https://atrio.esteri.it/"
  "https://www.senato.it/"
  "https://www.camera.it/"
  "https://www.italgiure.giustizia.it/sncass/"
  "https://bdp.giustizia.it/"
  "https://www.giustizia-amministrativa.it/"
  "https://openga.giustizia-amministrativa.it/"
  "https://www.cortecostituzionale.it/"
  "https://banchedati.corteconti.it/"
  "https://curia.europa.eu/"
  "https://hudoc.echr.coe.int/"
  "https://www.unifiedpatentcourt.org/en/decisions-and-orders"
  "https://www.cortedicassazione.it/it/massimario.page"
  "https://www.portaledelmassimario.ipzs.it/frontoffice/rassegneAnnuali.do"
  "https://www.agenziaentrate.gov.it/"
  "https://def.finanze.it/"
  "https://www.anticorruzione.it/"
  "https://www.ispettorato.gov.it/"
  "https://lavoro.gov.it/documenti-e-norme/interpelli/Pagine/default"
  "https://www.inps.it/"
  "https://www.gpdp.it/"
  "https://www.edpb.europa.eu/edpb_it"
  "https://www.bancaditalia.it/compiti/vigilanza/normativa/index.html"
  "https://www.ivass.it/"
  "https://www.consob.it/"
  "https://uif.bancaditalia.it/"
  "https://www.arbitrobancariofinanziario.it/"
  "https://www.acf.consob.it/"
  "https://www.agcm.it/"
  "https://www.cnel.it/Archivio-Contratti"
  "https://www.aranagenzia.it/"
  "https://www.mim.gov.it/"
  "https://libertaciviliimmigrazione.dlci.interno.gov.it/"
  "https://euaa.europa.eu/"
  "https://coi.euaa.europa.eu/"
  "https://www.uibm.gov.it/bancadati/"
  "https://register.epo.org/"
  "https://www.mimit.gov.it/"
)

errori=0
for url in "${URLS[@]}"; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 25 -A "Mozilla/5.0 (verifica-fonti)" "$url" || echo "000")
  case "$code" in
    2*|3*) stato="OK" ;;
    401|403|429) stato="ANTI-BOT (vivo, fetch bloccato)" ;;
    *) stato="ERRORE"; errori=$((errori+1)) ;;
  esac
  printf "%-10s %s %s\n" "[$code]" "$stato" "$url"
done

echo
if [ "$errori" -gt 0 ]; then
  echo "FALLITO: $errori fonti in errore. Aggiornare i cataloghi in references/."
  exit 1
fi
echo "OK: tutte le fonti rispondono (o sono vive dietro anti-bot)."
