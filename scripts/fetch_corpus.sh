#!/usr/bin/env bash
# Downloads the manual corpus to data/corpus (gitignored). Documents are manufacturer copyright,
# mirrored by Frank's Hospital Workshop for education. We index locally and never redistribute.
set -euo pipefail
BASE="http://www.frankshospitalworkshop.com/equipment"
UA="Mozilla/5.0 (Sieve corpus fetch; non-commercial; contact in README)"
fetch_page () { # $1 = index page, $2 = out dir, $3 = regex filter on filename
  curl -sL -A "$UA" "$BASE/$1.html" | grep -oiE 'href="[^"]+\.pdf"' | sed 's/href="//; s/"$//' | sort -u | grep -iE "$3" | while read -r rel; do
    name=$(basename "$rel"); out="$2/$name"
    [ -s "$out" ] && continue
    url="$BASE/$(python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe='/'))" "$rel")"
    curl -sL -A "$UA" --retry 2 -o "$out" "$url" || echo "FAILED $rel"
    sleep 0.5
  done
}
fetch_page oxygen_concentrators_service_manuals data/corpus/oxygen_concentrators 'service_manuals/|background/.*WHO'
fetch_page oxygen_concentrators_user_manuals   data/corpus/oxygen_concentrators 'EverFlo|DeVilbiss 525|Nuvo|NewLife|VisionAire|Platinum|Longfian|Lonfian|Oxymed|Sanrai|Yuwell'
fetch_page suction_pumps_service_manuals        data/corpus/suction_pumps       'service_manuals/'
fetch_page pulse_oximeter_service_manuals       data/corpus/pulse_oximeters     'service_manuals/.*(Nellcor|Masimo|Contec|Nonin|BPL|Mindray|Edan|Choice)'
echo "done"; du -sh data/corpus/*
