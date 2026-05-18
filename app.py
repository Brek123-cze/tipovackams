import streamlit as st
import pandas as pd
import time
import requests
import json
from datetime import datetime

st.set_page_config(page_title="MS v hokeji - Super Tipovačka", page_icon="🏒", layout="wide")

# Vstupní heslo pro celou partu
VSTUPNI_HESLO_APP = "d3105tr31ci"

if "uzivatel" not in st.session_state:
    # První kontrola: Je uživatel „ověřený“ pro vstup na web?
    if "overen_vstup" not in st.session_state:
        heslo_webu = st.text_input("Zadej společné heslo pro přístup na web:", type="password")
        if st.button("Vstoupit"):
            if heslo_webu == VSTUPNI_HESLO_APP:
                st.session_state["overen_vstup"] = True
                st.rerun()
            else:
                st.error("Chybné heslo webu!")
        st.stop() # Zastaví vykreslování zbytku stránky

ADMIN_HESLO = "hokej2026"
HRACI = ["Flesi", "Honza", "Jirka", "Karel", "Petr"]

# ⚠️ LINK NA GOOGLE APPS SCRIPT:
URL_API = "https://script.google.com/macros/s/AKfycbw8u_DCdQYGaH4iCQSJ7Zghq_60XTz7MPtIu4X1nAhQ-sCO-GHNig9ggJdPF437u65L/exec"

# --- ROZDĚLENÍ TÝMŮ DO SKUPIN ---
SKUPINA_A_TYMY = ["Finsko", "Švýcarsko", "Rakousko", "Lotyšsko", "Německo", "USA", "Maďarsko", "Velká Británie"]
SKUPINA_B_TYMY = ["Kanada", "Česko", "Slovensko", "Slovinsko", "Norsko", "Švédsko", "Dánsko", "Itálie"]

SOUPISKA_CR = [
    "Alscher Marek", "Beránek Ondřej", "Blümel Matěj", "Cibulka Tomáš", "Černoch Jiří",
    "Červenka Roman", "Flek Jakub", "Galvas Tomáš", "Hájek Libor", "Hronek Filip",
    "Chmelař Jaroslav", "Kaut Martin", "Kempný Michal", "Kořenář Josef", "Kovařčík Michal",
    "Kubalík Dominik", "Kváča Petr", "Mandát Jan", "Melovský Matyáš", "Pavlát Dominik",
    "Sedlák Lukáš", "Ščotka Jan", "Ticháček Jiří", "Tomášek David", "Voženílek Daniel"
]

ZAPASY_TYPY = ["Dán - ČR", "Slo - ČR", "Švé - ČR", "ČR - Itá", "Svk - ČR", "Nor - ČR", "ČR - Kan", "Čtvrtfinále", "Semifinále", "Finále / o 3. m."]

SLOUPCE_MATICE = []
for z in ZAPASY_TYPY:
    SLOUPCE_MATICE.extend([f"{z} (G)", f"{z} (A)"])

ZAPASY = [
    {"id": "1", "den": "15. 5. (Pátek)", "datum": "16:20", "domaci": "Finsko", "hoste": "Německo", "skupina": "A"},
    {"id": "2", "den": "15. 5. (Pátek)", "datum": "16:20", "domaci": "Švédsko", "hoste": "Kanada", "skupina": "B"},
    {"id": "3", "den": "15. 5. (Pátek)", "datum": "20:20", "domaci": "Švýcarsko", "hoste": "USA", "skupina": "A"},
    {"id": "4", "den": "15. 5. (Pátek)", "datum": "20:20", "domaci": "Dánsko", "hoste": "Česko", "skupina": "B"},
    {"id": "5", "den": "16. 5. (Sobota)", "datum": "12:20", "domaci": "Rakousko", "hoste": "Velká Británie", "skupina": "A"},
    {"id": "6", "den": "16. 5. (Sobota)", "datum": "12:20", "domaci": "Slovensko", "hoste": "Norsko", "skupina": "B"},
    {"id": "7", "den": "16. 5. (Sobota)", "datum": "16:20", "domaci": "Finsko", "hoste": "Maďarsko", "skupina": "A"},
    {"id": "8", "den": "16. 5. (Sobota)", "datum": "16:20", "domaci": "Kanada", "hoste": "Itálie", "skupina": "B"},
    {"id": "9", "den": "16. 5. (Sobota)", "datum": "20:20", "domaci": "Švýcarsko", "hoste": "Lotyšsko", "skupina": "A"},
    {"id": "10", "den": "16. 5. (Sobota)", "datum": "20:20", "domaci": "Slovinsko", "hoste": "Česko", "skupina": "B"},
    {"id": "11", "den": "17. 5. (Neděle)", "datum": "12:20", "domaci": "Velká Británie", "hoste": "USA", "skupina": "A"},
    {"id": "12", "den": "17. 5. (Neděle)", "datum": "12:20", "domaci": "Itálie", "hoste": "Slovensko", "skupina": "B"},
    {"id": "13", "den": "17. 5. (Neděle)", "datum": "16:20", "domaci": "Rakousko", "hoste": "Maďarsko", "skupina": "A"},
    {"id": "14", "den": "17. 5. (Neděle)", "datum": "16:20", "domaci": "Dánsko", "hoste": "Švédsko", "skupina": "B"},
    {"id": "15", "den": "17. 5. (Neděle)", "datum": "20:20", "domaci": "Německo", "hoste": "Lotyšsko", "skupina": "A"},
    {"id": "16", "den": "17. 5. (Neděle)", "datum": "20:20", "domaci": "Norsko", "hoste": "Slovinsko", "skupina": "B"},
    {"id": "17", "den": "18. 5. (Pondělí)", "datum": "16:20", "domaci": "Finsko", "hoste": "USA", "skupina": "A"},
    {"id": "18", "den": "18. 5. (Pondělí)", "datum": "16:20", "domaci": "Kanada", "hoste": "Dánsko", "skupina": "B"},
    {"id": "19", "den": "18. 5. (Pondělí)", "datum": "20:20", "domaci": "Německo", "hoste": "Švýcarsko", "skupina": "A"},
    {"id": "20", "den": "18. 5. (Pondělí)", "datum": "20:20", "domaci": "Švédsko", "hoste": "Česko", "skupina": "B"},
    {"id": "21", "den": "19. 5. (Úterý)", "datum": "16:20", "domaci": "Lotyšsko", "hoste": "Rakousko", "skupina": "A"},
    {"id": "22", "den": "19. 5. (Úterý)", "datum": "16:20", "domaci": "Itálie", "hoste": "Norsko", "skupina": "B"},
    {"id": "23", "den": "19. 5. (Úterý)", "datum": "20:20", "domaci": "Maďarsko", "hoste": "Velká Británie", "skupina": "A"},
    {"id": "24", "den": "19. 5. (Úterý)", "datum": "20:20", "domaci": "Slovinsko", "hoste": "Slovensko", "skupina": "B"},
    {"id": "25", "den": "20. 5. (Středa)", "datum": "16:20", "domaci": "Rakousko", "hoste": "Švýcarsko", "skupina": "A"},
    {"id": "26", "den": "20. 5. (Středa)", "datum": "16:20", "domaci": "Česko", "hoste": "Itálie", "skupina": "B"},
    {"id": "27", "den": "20. 5. (Středa)", "datum": "20:20", "domaci": "USA", "hoste": "Německo", "skupina": "A"},
    {"id": "28", "den": "20. 5. (Středa)", "datum": "20:20", "domaci": "Švédsko", "hoste": "Slovinsko", "skupina": "B"},
    {"id": "29", "den": "21. 5. (Čtvrtek)", "datum": "16:20", "domaci": "Lotyšsko", "hoste": "Finsko", "skupina": "A"},
    {"id": "30", "den": "21. 5. (Čtvrtek)", "datum": "16:20", "domaci": "Kanada", "hoste": "Norsko", "skupina": "B"},
    {"id": "31", "den": "21. 5. (Čtvrtek)", "datum": "20:20", "domaci": "Švýcarsko", "hoste": "Velká Británie", "skupina": "A"},
    {"id": "32", "den": "21. 5. (Čtvrtek)", "datum": "20:20", "domaci": "Dánsko", "hoste": "Slovensko", "skupina": "B"},
    {"id": "33", "den": "22. 5. (Pátek)", "datum": "16:20", "domaci": "Německo", "hoste": "Maďarsko", "skupina": "A"},
    {"id": "34", "den": "22. 5. (Pátek)", "datum": "16:20", "domaci": "Kanada", "hoste": "Slovinsko", "skupina": "B"},
    {"id": "35", "den": "22. 5. (Pátek)", "datum": "20:20", "domaci": "Finsko", "hoste": "Velká Británie", "skupina": "A"},
    {"id": "36", "den": "22. 5. (Pátek)", "datum": "20:20", "domaci": "Švédsko", "hoste": "Itálie", "skupina": "B"},
    {"id": "37", "den": "23. 5. (Sobota)", "datum": "12:20", "domaci": "Lotyšsko", "hoste": "USA", "skupina": "A"},
    {"id": "38", "den": "23. 5. (Sobota)", "datum": "12:20", "domaci": "Dánsko", "hoste": "Slovinsko", "skupina": "B"},
    {"id": "39", "den": "23. 5. (Sobota)", "datum": "16:20", "domaci": "Švýcarsko", "hoste": "Maďarsko", "skupina": "A"},
    {"id": "40", "den": "23. 5. (Sobota)", "datum": "16:20", "domaci": "Slovensko", "hoste": "Česko", "skupina": "B"},
    {"id": "41", "den": "23. 5. (Sobota)", "datum": "20:20", "domaci": "Rakousko", "hoste": "Německo", "skupina": "A"},
    {"id": "42", "den": "23. 5. (Sobota)", "datum": "20:20", "domaci": "Norsko", "hoste": "Švédsko", "skupina": "B"},
    {"id": "43", "den": "24. 5. (Neděle)", "datum": "16:20", "domaci": "Velká Británie", "hoste": "Lotyšsko", "skupina": "A"},
    {"id": "44", "den": "24. 5. (Neděle)", "datum": "16:20", "domaci": "Dánsko", "hoste": "Itálie", "skupina": "B"},
    {"id": "45", "den": "24. 5. (Neděle)", "datum": "20:20", "domaci": "Finsko", "hoste": "Rakousko", "skupina": "A"},
    {"id": "46", "den": "24. 5. (Neděle)", "datum": "20:20", "domaci": "Slovensko", "hoste": "Kanada", "skupina": "B"},
    {"id": "47", "den": "25. 5. (Pondělí)", "datum": "16:20", "domaci": "USA", "hoste": "Maďarsko", "skupina": "A"},
    {"id": "48", "den": "25. 5. (Pondělí)", "datum": "16:20", "domaci": "Česko", "hoste": "Norsko", "skupina": "B"},
    {"id": "49", "den": "25. 5. (Pondělí)", "datum": "20:20", "domaci": "Německo", "hoste": "Velká Británie", "skupina": "A"},
    {"id": "50", "den": "25. 5. (Pondělí)", "datum": "20:20", "domaci": "Slovinsko", "hoste": "Itálie", "skupina": "B"},
    {"id": "51", "den": "26. 5. (Úterý)", "datum": "12:20", "domaci": "Maďarsko", "hoste": "Lotyšsko", "skupina": "A"},
    {"id": "52", "den": "26. 5. (Úterý)", "datum": "12:20", "domaci": "Norsko", "hoste": "Dánsko", "skupina": "B"},
    {"id": "53", "den": "26. 5. (Úterý)", "datum": "16:20", "domaci": "USA", "hoste": "Rakousko", "skupina": "A"},
    {"id": "54", "den": "26. 5. (Úterý)", "datum": "16:20", "domaci": "Švédsko", "hoste": "Slovensko", "skupina": "B"},
    {"id": "55", "den": "26. 5. (Úterý)", "datum": "20:20", "domaci": "Švýcarsko", "hoste": "Finsko", "skupina": "A"},
    {"id": "56", "den": "26. 5. (Úterý)", "datum": "20:20", "domaci": "Česko", "hoste": "Kanada", "skupina": "B"},
]

DNY = []
for z in ZAPASY:
    if z["den"] not in DNY: DNY.append(z["den"])

def fetch_data_from_api(url):
    try:
        import random
        r = requests.get(f"{url}?nocache={random.randint(1, 100000)}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def nacti_vsechna_data():
    vysledky = {}
    tipy = {h: {} for h in HRACI}
    zolici = {h: {} for h in HRACI}
    celkove_tipy = {h: {
        "mistr": "", 
        "semifinale": ["", "", "", ""], 
        "cesko": "Základní skupina", 
        "mvp": "", 
        "goly": 0
    } for h in HRACI}
    kanadske_bodovani = {hrac: {col: 0 for col in SLOUPCE_MATICE} for hrac in SOUPISKA_CR}
    nastaveni = {"dlouhodobe_zamknuto": False}

    raw_json = fetch_data_from_api(URL_API)
    
    for row in raw_json:
        klic = str(row.get("Klíč", ""))
        if not klic: continue
        
        if klic == "nastaveni_dlouhodobe_zamknuto":
            try:
                nastaveni["dlouhodobe_zamknuto"] = bool(int(row.get("Hodnota1", 0)))
            except:
                pass
        
        elif klic.startswith("vysledky_"):
            z_id = klic.replace("vysledky_", "")
            try:
                vysledky[z_id] = {"d": int(row.get("Hodnota1", 0)), "h": int(row.get("Hodnota2", 0)), "pp_sn": bool(int(row.get("Hodnota3", 0)))}
            except:
                pass
            
        elif klic.startswith("tip_") and "_z_" in klic:
            casti = klic.split("_")
            hrac, z_id = casti[1], casti[3]
            if hrac in tipy:
                try:
                    tipy[hrac][z_id] = {"d": int(row.get("Hodnota1", 0)), "h": int(row.get("Hodnota2", 0))}
                except:
                    pass
                
        elif klic.startswith("zolik_"):
            casti = klic.split("_")
            hrac, z_id = casti[1], casti[3]
            if hrac in zolici:
                try:
                    zolici[hrac][z_id] = bool(int(row.get("Hodnota1", 0)))
                except:
                    pass
                
        elif klic.startswith("celkove_"):
            hrac = klic.replace("celkove_", "")
            if hrac in celkove_tipy:
                h1 = str(row.get("Hodnota1") if row.get("Hodnota1") is not None else "")
                h2 = str(row.get("Hodnota2") if row.get("Hodnota2") is not None else "")
                h3 = str(row.get("Hodnota3") if row.get("Hodnota3") is not None else "")
                h4 = str(row.get("Hodnota4") if row.get("Hodnota4") is not None else "")
                h5 = str(row.get("Hodnota5") if row.get("Hodnota5") is not None else "")
                h6 = str(row.get("Hodnota6") if row.get("Hodnota6") is not None else "Základní skupina")
                h7 = str(row.get("Hodnota7") if row.get("Hodnota7") is not None else "")
                h8 = row.get("Hodnota8")
                
                try:
                    goly_val = int(h8) if h8 and str(h8).strip().isdigit() else 0
                except:
                    goly_val = 0

                celkove_tipy[hrac] = {
                    "mistr": h1,
                    "semifinale": [h2, h3, h4, h5],
                    "cesko": h6 if h6 in ["Základní skupina", "Čtvrtfinále", "Semifinále", "Bronz", "Stříbro", "Zlato 🥇"] else "Základní skupina",
                    "mvp": h7,
                    "goly": goly_val
                }
                
        elif klic.startswith("stats_"):
            hrac_jmeno = klic.replace("stats_", "")
            if hrac_jmeno in kanadske_bodovani:
                for col in SLOUPCE_MATICE:
                    if col in row and row[col] != "":
                        try:
                            kanadske_bodovani[hrac_jmeno][col] = int(float(row[col]))
                        except:
                            kanadske_bodovani[hrac_jmeno][col] = 0

    return {"vysledky": vysledky, "tipy": tipy, "zolici": zolici, "celkove_tipy": celkove_tipy, "kanadske_bodovani": kanadske_bodovani, "nastaveni": nastaveni}

def uloz_do_google_sheets(aktualni_data):
    rows = []
    
    # Uložení stavu zámku
    rows.append({
        "Klíč": "nastaveni_dlouhodobe_zamknuto", 
        "Hodnota1": int(aktualni_data.get("nastaveni", {}).get("dlouhodobe_zamknuto", False))
    })
    
    for k, v in aktualni_data["vysledky"].items():
        rows.append({"Klíč": f"vysledky_{k}", "Hodnota1": int(v["d"]), "Hodnota2": int(v["h"]), "Hodnota3": int(v["pp_sn"])})
        
    for hrac in HRACI:
        for z_id, v in aktualni_data["tipy"][hrac].items():
            rows.append({"Klíč": f"tip_{hrac}_z_{z_id}", "Hodnota1": int(v["d"]), "Hodnota2": int(v["h"])})
        for z_id, v in aktualni_data["zolici"][hrac].items():
            rows.append({"Klíč": f"zolik_{hrac}_z_{z_id}", "Hodnota1": int(v)})
            
        ct = aktualni_data["celkove_tipy"][hrac]
        semifinale_list = ct.get("semifinale", ["", "", "", ""])
        while len(semifinale_list) < 4: semifinale_list.append("")
            
        rows.append({
            "Klíč": f"celkove_{hrac}", 
            "Hodnota1": ct.get("mistr", ""), 
            "Hodnota2": semifinale_list[0], "Hodnota3": semifinale_list[1], 
            "Hodnota4": semifinale_list[2], "Hodnota5": semifinale_list[3], 
            "Hodnota6": ct.get("cesko", "Základní skupina"), "Hodnota7": ct.get("mvp", ""), 
            "Hodnota8": int(ct.get("goly", 0)) if ct.get("goly") else 0
        })
        
    for hrac in SOUPISKA_CR:
        r = {"Klíč": f"stats_{hrac}"}
        for col in SLOUPCE_MATICE:
            val = aktualni_data["kanadske_bodovani"].get(hrac, {}).get(col, 0)
            r[col] = int(val) if val else 0
        rows.append(r)
        
    try:
        requests.post(URL_API, json=rows, timeout=15)
    except:
        st.error("Nepodařilo se navázat spojení s Google Diskem. Zkus to za chvíli.")
        
data = nacti_vsechna_data()

# --- LOGIKA BODOVÁNÍ PRO HRÁČE ---
def spocitej_body_hrace(tip_d, tip_h, real_d, real_h, zolik=False, real_pp_sn=False):
    if tip_d is None or tip_h is None or real_d is None or real_h is None:
        return 0, False

    if real_pp_sn:
        min_goly = min(real_d, real_h)
        real_d_efektivni = min_goly
        real_h_efektivni = min_goly
    else:
        real_d_efektivni = real_d
        real_h_efektivni = real_h

    vitez_tip = "D" if tip_d > tip_h else ("H" if tip_h > tip_d else "R")
    vitez_real = "D" if real_d_efektivni > real_h_efektivni else ("H" if real_h_efektivni > real_d_efektivni else "R")
    
    rozdil_tip = tip_d - tip_h
    rozdil_real = real_d_efektivni - real_h_efektivni
    
    goly_tip = tip_d + tip_h
    goly_real = real_d_efektivni + real_h_efektivni

    body = 0
    presny = False

    if tip_d == real_d_efektivni and tip_h == real_h_efektivni:
        body = 10
        presny = True
    elif (vitez_tip == vitez_real and rozdil_tip == rozdil_real) or \
         (vitez_tip == vitez_real and goly_tip == goly_real) or \
         (vitez_real == "R" and vitez_tip == "R"):
        body = 6
    elif vitez_tip == vitez_real:
        body = 4
    elif goly_tip == goly_real:
        body = 2
    else:
        body = 0

    if zolik:
        if body > 0:
            body = body * 2
        else:
            body = -2

    return body, presny

def generuj_tabulky_ms(data_turnaje):
    tab_a = {t: [0, 0, 0] for t in SKUPINA_A_TYMY}
    tab_b = {t: [0, 0, 0] for t in SKUPINA_B_TYMY}
    celkem_golu = 0
    
    for z in ZAPASY:
        z_id = z["id"]
        if z_id in data_turnaje["vysledky"]:
            res = data_turnaje["vysledky"][z_id]
            d_goly = int(res.get("d", 0))
            h_goly = int(res.get("h", 0))
            je_pp_sn = res.get("pp_sn", False)
            celkem_golu += (d_goly + h_goly)
            
            if d_goly > h_goly:
                d_body = 2 if je_pp_sn else 3
                h_body = 1 if je_pp_sn else 0
            elif h_goly > d_goly:
                d_body = 1 if je_pp_sn else 0
                h_body = 2 if je_pp_sn else 3
            else:
                d_body, h_body = 1, 1
                
            target_tab = tab_a if z["skupina"] == "A" else tab_b
            if z["domaci"] in target_tab:
                target_tab[z["domaci"]][0] += d_body
                target_tab[z["domaci"]][1] += (d_goly - h_goly)
                target_tab[z["domaci"]][2] += d_goly
            if z["hoste"] in target_tab:
                target_tab[z["hoste"]][0] += h_body
                target_tab[z["hoste"]][1] += (h_goly - d_goly)
                target_tab[z["hoste"]][2] += h_goly
                
    df_a = pd.DataFrame([{"Tým": k, "Body": v[0], "Skóre +/-": v[1], "Góly": v[2]} for k, v in tab_a.items()]).sort_values(by=["Body", "Skóre +/-", "Góly"], ascending=False).reset_index(drop=True)
    df_b = pd.DataFrame([{"Tým": k, "Body": v[0], "Skóre +/-": v[1], "Góly": v[2]} for k, v in tab_b.items()]).sort_values(by=["Body", "Skóre +/-", "Góly"], ascending=False).reset_index(drop=True)
    return df_a, df_b, celkem_golu

def ziskej_dataframe_statistik(data_turnaje):
    radky = []
    for hrac in SOUPISKA_CR:
        g_celkem = 0
        a_celkem = 0
        for z in ZAPASY_TYPY:
            g_celkem += data_turnaje["kanadske_bodovani"].get(hrac, {}).get(f"{z} (G)", 0)
            a_celkem += data_turnaje["kanadske_bodovani"].get(hrac, {}).get(f"{z} (A)", 0)
        
        r = {"Hráč": hrac}
        for col in SLOUPCE_MATICE:
            r[col] = data_turnaje["kanadske_bodovani"].get(hrac, {}).get(col, 0)
        r["Celkem Góly"] = g_celkem
        r["Celkem Asistence"] = a_celkem
        r["Celkem Body (G+A)"] = g_celkem + a_celkem
        radky.append(r)
    return pd.DataFrame(radky)

def urci_nejlepsi_hrace(df_stats):
    df_filtered = df_stats[df_stats["Celkem Body (G+A)"] > 0]
    if df_filtered.empty: return "Nikdo"
    df_sorted = df_filtered.sort_values(by=["Celkem Body (G+A)", "Celkem Góly"], ascending=False)
    max_body = df_sorted.iloc[0]["Celkem Body (G+A)"]
    max_goly = df_sorted.iloc[0]["Celkem Góly"]
    top_hraci = df_sorted[(df_sorted["Celkem Body (G+A)"] == max_body) & (df_sorted["Celkem Góly"] == max_goly)]
    vystup = [f"{r['Hráč']} ({r['Celkem Body (G+A)']} b. / {r['Celkem Góly']}+{r['Celkem Asistence']})" for _, r in top_hraci.iterrows()]
    return ", ".join(vystup)

sorted_skupina_a, sorted_skupina_b, celkove_goly_ms = generuj_tabulky_ms(data)
df_statistiky = ziskej_dataframe_statistik(data)
nejlepsi_cesi_output = urci_nejlepsi_hrace(df_statistiky)

statistiky_hracu = {h: {"body": 0, "presne": 0} for h in HRACI}
for hrac in HRACI:
    for z in ZAPASY:
        z_id = z["id"]
        if z_id in data["vysledky"] and z_id in data["tipy"][hrac]:
            t = data["tipy"][hrac][z_id]
            r = data["vysledky"][z_id]
            zolik = data["zolici"][hrac].get(z_id, False)
            if t.get("d") is not None and r.get("d") is not None:
                b, p = spocitej_body_hrace(t["d"], t["h"], r["d"], r["h"], zolik, r.get("pp_sn", False))
                statistiky_hracu[hrac]["body"] += b
                if p: statistiky_hracu[hrac]["presne"] += 1

if "uzivatel" not in st.session_state:
    st.title("🏒 MS v hokeji - Tipovačka")
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    with c_mid:
        vybrany = st.selectbox("Vyber své jméno:", ["-- Vyber --"] + HRACI + ["Správce 👑"])
        if vybrany != "-- Vyber --":
            if vybrany == "Správce 👑":
                heslo = st.text_input("Heslo:", type="password")
                if st.button("Vstoupit jako správce") and heslo == ADMIN_HESLO:
                    st.session_state["uzivatel"] = "admin"
                    st.rerun()
            else:
                if st.button(f"Vstoupit jako {vybrany}"):
                    st.session_state["uzivatel"] = vybrany
                    st.rerun()
    st.stop()

current_user = st.session_state["uzivatel"]

# --- NAVIGACE VPRAVO NAHOŘE ---
st.markdown(
    f"<div style='background-color: #1e3d59; padding: 12px; border-radius: 8px; margin-bottom: 20px; color: white; display: flex; justify-content: space-between; align-items: center;'>"
    f"<h3 style='margin:0; color:white;'>🏒 MS v hokeji 2026</h3>"
    f"<span>Přihlášen: <b>{current_user if current_user != 'admin' else 'Správce 👑'}</b></span>"
    f"</div>", 
    unsafe_allow_html=True
)

menu_options = ["Žebříček hráčů 🏆", "Moje tipy (Zápasy) 📝", "Celoturnajové tipy 🏆", "Tipy ostatních 👀"]
if current_user == "admin":
    menu_options.extend(["Zadávání výsledků", "Správa statistik ČR (Excel matice)"])

volba = st.sidebar.radio("Navigace aplikace:", menu_options)

if st.sidebar.button("Odhlásit se 🚪"):
    del st.session_state["uzivatel"]
    st.rerun()

# --- 1. ZÁLOŽKA: ŽEBŘÍČEK ---
if volba == "Žebříček hráčů 🏆":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("🏆 Průběžný žebříček tipovačky")
        zebricek = [{"jmeno": h, "body": v["body"], "presne": v["presne"]} for h, v in statistiky_hracu.items()]
        zebricek = sorted(zebricek, key=lambda x: (x["body"], x["presne"]), reverse=True)
        
        for idx, p in enumerate(zebricek):
            medaile = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🔵"
            st.markdown(f"<div style='background-color: rgba(30,61,89,0.05); padding: 8px; border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between;'><b>{medaile} {idx+1}. {p['jmeno']}</b><span><b>{p['body']} B</b> (🎯 {p['presne']}x)</span></div>", unsafe_allow_html=True)
            
        st.write("")
        with st.expander("🔍 Rozbalit detailní bodování hráčů (zápas po zápase)"):
            vybrany_hrac = st.selectbox("Vyber hráče pro detail bodů:", HRACI)
            if vybrany_hrac:
                zapas_body = {}
                for z in ZAPASY:
                    z_id = str(z["id"])
                    res = data["vysledky"].get(z_id)
                    tip = data["tipy"][vybrany_hrac].get(z_id)
                    zolik = data["zolici"][vybrany_hrac].get(z_id, False)
                    if res and tip and tip["d"] is not None and tip["h"] is not None:
                        b, _ = spocitej_body_hrace(tip["d"], tip["h"], res["d"], res["h"], zolik, bool(res.get("pp_sn", False)))
                        zapas_body[int(z_id)] = b
                    else:
                        zapas_body[int(z_id)] = 0
                radky_list = []
                for r in range(1, 9):
                    radek = {}
                    for c in range(7):
                        z_index = r + (c * 8)
                        if z_index <= len(ZAPASY):
                            z_info = ZAPASY[z_index - 1]
                            tymy = f"{z_info['domaci'][0:3]}. - {z_info['hoste'][0:3]}."
                            radek[f"Zápas (sk. {c+1})"] = f"Z{z_index} ({tymy})"
                            radek[f"Body (sk. {c+1})"] = f"{zapas_body.get(z_index, 0)} b"
                        else:
                            radek[f"Zápas (sk. {c+1})"] = "-"
                            radek[f"Body (sk. {c+1})"] = "-"
                    radky_list.append(radek)
                df_detail = pd.DataFrame(radky_list)
                st.dataframe(df_detail, use_container_width=True, hide_index=True)
                
        st.write("---")
        st.subheader("📊 Statistiky MS v hokeji")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Skupina A**")
            st.dataframe(sorted_skupina_a, hide_index=True, use_container_width=True)
        with c2:
            st.write("**Skupina B**")
            st.dataframe(sorted_skupina_b, hide_index=True, use_container_width=True)
            
        st.info(f"🚨 **Celkový počet gólů vstřelených na celém šampionátu:** {celkove_goly_ms} gólů")
        st.success(f"🌟 **Nejlepší střelec / lídr bodování ČR:** {nejlepsi_cesi_output}")
        
        # --- NOVINKA: Kdo z tipujících vsadil na nejlepší české hráče? ---
        st.write("### 🎯 Kdo tyto lídry natipoval jako své celkové MVP?")
        
        # Vytáhneme jména aktuálních lídrů z textového výstupu
        # (Odstraníme závorky s body, abychom měli čistá jména pro porovnání)
        aktualni_lidri = []
        if nejlepsi_cesi_output != "Nikdo":
            for kousek in nejlepsi_cesi_output.split(", "):
                jmeno_lidra = kousek.split(" (")[0].strip()
                aktualni_lidri.append(jmeno_lidra)
        
        # Poskládáme přehled, kdo koho reálně z party tipoval
        mvp_radky = []
        for hrac in HRACI:
            # Načteme, koho má daný hráč uloženého pod klíčem "mvp"
            natipovane_mvp = data.get("celkove_tipy", {}).get(hrac, {}).get("mvp", "-").strip()
            
            # Pokud se tip shoduje s jedním z aktuálních lídrů, dáme k tomu fajfku a zvýrazníme ho
            je_trefa = "✅" if any(lidr in natipovane_mvp for lidr in aktualni_lidri) and natipovane_mvp != "-" else "❌"
            
            mvp_radky.append({
                "Tipující hráč": hrac,
                "Jeho dlouhodobý tip na MVP": natipovane_mvp,
                "Aktuální trefa?": je_trefa
            })
            
        df_mvp_srovnani = pd.DataFrame(mvp_radky)
        st.dataframe(df_mvp_srovnani, use_container_width=True, hide_index=True)

# --- 2. ZÁLOŽKA: MOJE TIPY (ZÁPASY) ---
elif volba == "Moje tipy (Zápasy) 📝":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("📝 Tipování zápasů")
        vybrany_den = st.selectbox("Vyber hrací den:", DNY)
        st.write(f"### Zápasy pro: {vybrany_den}")
        st.info("Změň skóre, zaškrtni žolíka a pak vše odešli naráz jedním kliknutím dole.")
        
        aktivni_zolik_dnes = None
        for z in ZAPASY:
            if z["den"] == vybrany_den and data["zolici"][current_user].get(z["id"], False):
                aktivni_zolik_dnes = z["id"]
                
        with st.form("tipy_zapasu_form"):
            docasne_tipy = {}
            docasni_zolici = {}
            for z in ZAPASY:
                if z["den"] != vybrany_den: continue
                z_id = z["id"]
                
                zapas_odehran = z_id in data["vysledky"]
                st.write(f"**{z['datum']} | {z['domaci']} vs. {z['hoste']}**")
                stary_d = data["tipy"][current_user].get(z_id, {}).get("d", 0)
                stary_h = data["tipy"][current_user].get(z_id, {}).get("h", 0)
                
                # --- KONTROLA ČASU ZAHÁJENÍ ZÁPASU (Opravené párování textu) ---
                import datetime as dt_lib
                aktualni_cas = dt_lib.datetime.now()
                
                # Vygenerujeme dnešní den bez mezer (např. "18.5.")
                dnes_cisty1 = aktualni_cas.strftime("%d.%m.").replace("0", "")
                dnes_cisty2 = f"{aktualni_cas.day}.{aktualni_cas.month}."
                
                # Očistíme text vybraného dne v roletce, abychom v něm mohli hledat (např. "18.5.(pondělí)")
                vybrany_den_cisty = vybrany_den.replace(" ", "")
                
                zapas_uzamcen = False
                # Pokud vybraný den v roletce obsahuje dnešní datum, zapínáme hodinový zámek
                je_dnes = (dnes_cisty1 in vybrany_den_cisty or dnes_cisty2 in vybrany_den_cisty)
                
                if je_dnes:
                    try:
                        cas_obj = dt_lib.datetime.strptime(z["datum"].strip(), "%H:%M")
                        cas_zapasu = aktualni_cas.replace(hour=cas_obj.hour, minute=cas_obj.minute, second=0, microsecond=0)
                        zapas_uzamcen = aktualni_cas > cas_zapasu
                    except:
                        zapas_uzamcen = False
                else:
                    zapas_uzamcen = False
                    
                if data["vysledky"].get(str(z["id"]), {}).get("vyhodnoceno", False):
                    zapas_uzamcen = True
                    
                je_zamknuto = bool(zapas_uzamcen or zapas_odehran)
                
                c1, c2, c3 = st.columns([1, 1, 2])
                tip_d = c1.number_input(f"Skóre {z['domaci']}", min_value=0, value=int(stary_d), key=f"d_{z_id}", disabled=je_zamknuto)
                tip_h = c2.number_input(f"Skóre {z['hoste']}", min_value=0, value=int(stary_h), key=f"h_{z_id}", disabled=je_zamknuto)
                je_z = (aktivni_zolik_dnes == z_id)
                zolik = c3.checkbox("💥 Žolík dne", value=je_z, key=f"z_{z_id}", disabled=je_zamknuto)
                
                docasne_tipy[z_id] = {"d": tip_d, "h": tip_h}
                docasni_zolici[z_id] = zolik
                if je_zamknuto:
                    st.caption("🔒 Tento zápas již byl zahájen nebo vyhodnocen, tipy jsou uzamčeny.")
                st.write("---")
                
            ulozit_button = st.form_submit_button("Uložit zápis zápasů do tabulky 💾")
            
        if ulozit_button:
            with st.spinner("Ukládám tvoje tipy na Disk..."):
                zvoleny_zolik_id = None
                for z_id, status in docasni_zolici.items():
                    if status:
                        zvoleny_zolik_id = z_id
                        break
                for z_id, skore in docasne_tipy.items():
                    data["tipy"][current_user][z_id] = skore
                for z in ZAPASY:
                    if z["den"] == vybrany_den:
                        data["zolici"][current_user][z["id"]] = (z["id"] == zvoleny_zolik_id)
                uloz_do_google_sheets(data)
                st.success("Tipy pro vybraný den uloženy do Google Tabulky!")
                time.sleep(0.5)
                st.rerun()

        # --- NOVÁ DYNAMICKÁ TABULKA MVP S AKTUÁLNÍMI STATISTIKAMI ---
        st.write("### 🏒 Jak si vedou vaši favorité na nejužitečnějšího hráče (MVP)?")
        
        mvp_radky = []
        for hrac in HRACI:
            # Načteme dlouhodobý tip na MVP od konkrétního tipujícího
            natipovane_mvp = data.get("celkove_tipy", {}).get(hrac, {}).get("mvp", "-").strip()
            
            # Pokusíme se najít tohoto zapsaného hráče v naší matici statistik
            stats_hledaneho_hrace = "-"
            if natipovane_mvp != "-":
                # Prohledáme soupisku, jestli zadaný text sedí (např. obsahuje příjmení)
                nalezeny_hrac_na_soupisce = None
                for c_hrac in SOUPISKA_CR:
                    if c_hrac.lower() in natipovane_mvp.lower() or natipovane_mvp.lower() in c_hrac.lower():
                        nalezeny_hrac_na_soupisce = c_hrac
                        break
                
                # Pokud jsme hráče našli, vytáhneme z df_statistiky jeho reálná čísla
                if nalezeny_hrac_na_soupisce and not df_statistiky.empty:
                    hrac_row = df_statistiky[df_statistiky["Hráč"] == nalezeny_hrac_na_soupisce]
                    if not hrac_row.empty:
                        goly = int(hrac_row.iloc[0]["Celkem Góly"])
                        asistence = int(hrac_row.iloc[0]["Celkem Asistence"])
                        body = int(hrac_row.iloc[0]["Celkem Body (G+A)"])
                        stats_hledaneho_hrace = f"⭐ {goly} + {asistence} = {body} b."
                    else:
                        stats_hledaneho_hrace = "0 + 0 = 0 b."
                else:
                    stats_hledaneho_hrace = "0 + 0 = 0 b. (mimo soupisku ČR)"
            
            mvp_radky.append({
                "Tipující parťák": hrac,
                "Jeho celkový tip na MVP": natipovane_mvp,
                "Aktuální bilance v turnaji (G+A=B)": stats_hledaneho_hrace
            })
            
        df_mvp_srovnani = pd.DataFrame(mvp_radky)
        st.dataframe(df_mvp_srovnani, use_container_width=True, hide_index=True)

# --- 3. ZÁLOŽKA: CELOTURNAJOVÉ TIPY ---
elif volba == "Celoturnajové tipy 🏆":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("🏆 Celoturnajové dlouhodobé tipy")
        
        je_zamknuto_spravcem = data.get("nastaveni", {}).get("dlouhodobe_zamknuto", False)
        if current_user == "admin":
            dlouhodobe_disabled = False
        else:
            dlouhodobe_disabled = je_zamknuto_spravcem
            
        # Načtení starých hodnot ze struktury
        ct = data["celkove_tipy"].get(current_user, {})
        stary_mistr = ct.get("mistr", "")
        semi_list = ct.get("semifinale", ["", "", "", ""])
        while len(semi_list) < 4: semi_list.append("")
        stary_cesko = ct.get("cesko", "Základní skupina")
        stary_mvp = ct.get("mvp", "")
        stary_goly = ct.get("goly", 0)
        
        with st.form("dlouhodobe_tipy_form"):
            st.write("### Vyplň své celoturnajové tipy")
            
            tip_mistr = st.text_input("Celkový vítěz turnaje 🏆", value=stary_mistr, disabled=dlouhodobe_disabled)
            
            st.write("**4 semifinalisté (týmy, které postoupí do bojů o medaile) 🏒**")
            semi1 = st.text_input("Semifinalista 1", value=semi_list[0], disabled=dlouhodobe_disabled)
            semi2 = st.text_input("Semifinalista 2", value=semi_list[1], disabled=dlouhodobe_disabled)
            semi3 = st.text_input("Semifinalista 3", value=semi_list[2], disabled=dlouhodobe_disabled)
            semi4 = st.text_input("Semifinalista 4", value=semi_list[3], disabled=dlouhodobe_disabled)
            
            faze_options = ["Základní skupina", "Čtvrtfinále", "Semifinále", "Bronz", "Stříbro", "Zlato 🥇"]
            if stary_cesko not in faze_options: stary_cesko = "Základní skupina"
            tip_cesko = st.selectbox("Kam až dojde český tým? 🇨🇿", options=faze_options, index=faze_options.index(stary_cesko), disabled=dlouhodobe_disabled)
            
            tip_mvp = st.text_input("Nejužitečnější hráč turnaje (MVP) 🌟", value=stary_mvp, disabled=dlouhodobe_disabled)
            tip_goly = st.number_input("Celkový počet gólů v celém turnaji 🥅", min_value=0, value=int(stary_goly), step=1, disabled=dlouhodobe_disabled)
            
            uloz_dl_button = st.form_submit_button("Uložit celoturnajové tipy 💾")
            
        if uloz_dl_button:
            data["celkove_tipy"][current_user] = {
                "mistr": tip_mistr,
                "semifinale": [semi1, semi2, semi3, semi4],
                "cesko": tip_cesko,
                "mvp": tip_mvp,
                "goly": int(tip_goly)
            }
            uloz_do_google_sheets(data)
            st.success("Tipy úspěšně uloženy!")
            time.sleep(0.5)
            st.rerun()
            
        if je_zamknuto_spravcem and current_user != "admin":
            st.error("🔒 Dlouhodobé tipy byly uzamčeny správcem, hodnoty již nelze upravovat.")

# --- 4. ZÁLOŽKA: TIPY OSTATNÍCH ---
elif volba == "Tipy ostatních 👀":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("👀 Co tipovali soupeři?")
        kat = st.radio("Vyber kategorii:", ["Denní zápasy", "Celoturnajové tipy"])
        
        if kat == "Denní zápasy":
            v_den = st.selectbox("Vyber hrací den:", DNY, key="view_den")
            for z in ZAPASY:
                if z["den"] != v_den: continue
                z_id = z["id"]
                st.write(f"**{z['domaci']} vs. {z['hoste']}** ({z['datum']})")
                odehran = z_id in data["vysledky"]
                if odehran:
                    pripona = " (PP/SN)" if data["vysledky"][z_id].get("pp_sn", False) else ""
                    st.write(f"🏁 *Výsledek:* `{data['vysledky'][z_id]['d']} : {data['vysledky'][z_id]['h']}`**{pripona}**")
                for hrac in HRACI:
                    if hrac == current_user: continue
                    t = data["tipy"][hrac].get(z_id, {"d": "-", "h": "-"})
                    zol = " 🔥" if data["zolici"][hrac].get(z_id, False) else ""
                    if odehran:
                        st.write(f"• {hrac}: **{t['d']} : {t['h']}**{zol}")
                    else:
                        st.write(f"• {hrac}: *? : ?* (Utajeno)")
                st.write("---")
        else:
            st.write("### 📊 Kompletní pevná tabulka dlouhodobých tipů")
            
            kategorie = [
                "Celkový vítěz 🏆", 
                "Semifinalista 1 🏒", 
                "Semifinalista 2 🏒", 
                "Semifinalista 3 🏒", 
                "Semifinalista 4 🏒", 
                "Konečná fáze ČR 🇨🇿", 
                "Nejužitečnější hráč (MVP) 🌟", 
                "Celkový počet gólů 🥅"
            ]
            
            tabulka_data = {}
            for hrac in HRACI:
                ct = data["celkove_tipy"].get(hrac, {})
                s_list = ct.get("semifinale", ["-", "-", "-", "-"])
                while len(s_list) < 4: s_list.append("-")
                
                hrac_sloupec = [
                    str(ct.get("mistr", "-")),
                    str(s_list[0] if s_list[0] else "-"),
                    str(s_list[1] if s_list[1] else "-"),
                    str(s_list[2] if s_list[2] else "-"),
                    str(s_list[3] if s_list[3] else "-"),
                    str(ct.get("cesko", "-")),
                    str(ct.get("mvp", "-")),
                    str(ct.get("goly", "-"))
                ]
                tabulka_data[hrac] = hrac_sloupec
                
            df_dlouhodobe = pd.DataFrame(tabulka_data, index=kategorie)
            st.dataframe(df_dlouhodobe, use_container_width=True)
            
            if data.get("nastaveni", {}).get("dlouhodobe_zamknuto", False):
                st.caption("🔒 Dlouhodobé tipy byly správcem kompletně uzamčeny.")

# --- 5. ADMIN ZÁLOŽKA: ZADÁVÁNÍ VÝSLEDKŮ ---
elif volba == "Zadávání výsledků" and current_user == "admin":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("👑 Administrace: Zadávání reálných výsledků")
        v_den = st.selectbox("Vyber den zápasů:", DNY)
        
        with st.form("admin_vysledky_form"):
            st.write(f"### Reálné zápasy pro den: {v_den}")
            docasne_vysledky = {}
            
            for z in ZAPASY:
                if z["den"] != v_den: continue
                z_id = z["id"]
                st.write(f"**{z['domaci']} vs. {z['hoste']}**")
                stary_d = data["vysledky"].get(z_id, {}).get("d", 0)
                stary_h = data["vysledky"].get(z_id, {}).get("h", 0)
                stare_pp = data["vysledky"].get(z_id, {}).get("pp_sn", False)
                
                c1, c2, c3 = st.columns([1, 1, 2])
                r_d = c1.number_input("Skóre Domácí", min_value=0, value=int(stary_d), key=f"r_d_{z_id}")
                r_h = c2.number_input("Skóre Hosté", min_value=0, value=int(stary_h), key=f"r_h_{z_id}")
                pp_sn = c3.checkbox("Prodloužení / Nájezdy (PP/SN)", value=stare_pp, key=f"pp_{z_id}")
                odehrano = c3.checkbox("Odehráno / Vyhodnotit", value=(z_id in data["vysledky"]), key=f"o_{z_id}")
                
                docasne_vysledky[z_id] = {"d": r_d, "h": r_h, "pp_sn": pp_sn, "aktivni": odehrano}
                st.write("---")
                
            admin_ulozit_button = st.form_submit_button("Uložit zápasy a přepočítat celou aplikaci 🔄")
            
        if admin_ulozit_button:
            with st.spinner("Ukládám výsledky..."):
                for z_id, v in docasne_vysledky.items():
                    if v["aktivni"]:
                        data["vysledky"][z_id] = {"d": v["d"], "h": v["h"], "pp_sn": v["pp_sn"], "vyhodnoceno": True}
                    else:
                        if z_id in data["vysledky"]: del data["vysledky"][z_id]
                uloz_do_google_sheets(data)
                st.success("Zápasy uloženy a přepočítány!")
                time.sleep(0.5)
                st.rerun()

        st.write("## 🔒 Správa uzamčení dlouhodobých tipů")
        aktualni_zamek = data.get("nastaveni", {}).get("dlouhodobe_zamknuto", False)
        
        with st.form("admin_zamek_form"):
            zamknout_dl_tipy = st.checkbox("Uzamknout dlouhodobé tipy pro všechny hráče", value=aktualni_zamek)
            tlacitko_zamku = st.form_submit_button("Uložit nastavení zámku 💾")
            
        if tlacitko_zamku:
            data["nastaveni"]["dlouhodobe_zamknuto"] = zamknout_dl_tipy
            uloz_do_google_sheets(data)
            st.success("Nastavení zámku dlouhodobých tipů uloženo!")
            time.sleep(0.5)
            st.rerun()

# --- 6. ADMIN ZÁLOŽKA: EXCEL MATICE STATISTIK ČR ---
elif volba == "Správa statistik ČR (Excel matice)" and current_user == "admin":
    st.title("👑 Administrace: Kanadské bodování")
    df_editor_input = df_statistiky.drop(columns=["Celkem Góly", "Celkem Asistence", "Celkem Body (G+A)"])
    
    konfigurace_sloupcu = {"Hráč": st.column_config.TextColumn("Hráč", width=180, disabled=True)}
    for col in SLOUPCE_MATICE:
        konfigurace_sloupcu[col] = st.column_config.NumberColumn(col, width=45, min_value=0, step=1)
    
    with st.form("excel_stats_form"):
        upraveny_df = st.data_editor(df_editor_input, key="excel_stats_editor", use_container_width=True, hide_index=True, column_config=konfigurace_sloupcu)
        tlacitko_ulozit = st.form_submit_button("Uložit celou tabulku statistik najednou 💾")
        
    if tlacitko_ulozit:
        with st.spinner("Synchronizuji statistiky hráčů na Disk..."):
            for _, radek in upraveny_df.iterrows():
                hrac = radek["Hráč"]
                for col in SLOUPCE_MATICE:
                    data["kanadske_bodovani"][hrac][col] = int(radek[col])
            uloz_do_google_sheets(data)
            st.success("Statistiky kanadského bodování byly uloženy do Google Sheets!")
            time.sleep(0.5)
            st.rerun()
