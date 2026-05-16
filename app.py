import streamlit as st
import pandas as pd
import time
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="MS v hokeji - Super Tipovačka", page_icon="🏒", layout="wide")

ADMIN_HESLO = "hokej2026"
HRACI = ["Flesi", "Honza", "Jirka", "Karel", "Petr"]

# --- ROZDĚLENÍ TÝMŮ DO SKUPIN ---
SKUPINA_A_TYMY = ["Finsko", "Švýcarsko", "Rakousko", "Lotyšsko", "Německo", "USA", "Maďarsko", "Velká Británie"]
SKUPINA_B_TYMY = ["Kanada", "Česko", "Slovensko", "Slovinsko", "Norsko", "Švédsko", "Dánsko", "Itálie"]

# --- PŘESNÁ SOUPISKA Z TVÉHO OBRÁZKU ---
SOUPISKA_CR = [
    "Alscher Marek", "Beránek Ondřej", "Blümel Matěj", "Cibulka Tomáš", "Černoch Jiří",
    "Červenka Roman", "Flek Jakub", "Galvas Tomáš", "Hájek Libor", "Hronek Filip",
    "Chmelař Jaroslav", "Kaut Martin", "Kempný Michal", "Kořenář Josef", "Kovařčík Michal",
    "Kubalík Dominik", "Kváča Petr", "Mandát Jan", "Melovský Matyáš", "Pavlát Dominik",
    "Sedlák Lukáš", "Ščotka Jan", "Ticháček Jiří", "Tomášek David", "Voženílek Daniel"
]

ZAPASY_TYPY = ["Švy - ČR", "Nor - ČR", "ČR - Dán", "ČR - Maď", "Zápas 5", "Zápas 6", "Zápas 7", "Čtvrtfinále", "Semifinále", "Finále / o 3. m."]

SLOUPCE_MATICE = []
for z in ZAPASY_TYPY:
    SLOUPCE_MATICE.extend([f"{z} (G)", f"{z} (A)"])

# --- KOMPLETNÍ SEZNAM ZÁPASŮ ---
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

# --- PROPOJENÍ S GOOGLE SHEETS JEDNÍM KLIKNUTÍM ---
conn = st.connection("gsheets", type=GSheetsConnection)

def nacti_vsechna_data():
    try:
        # Zkusíme načíst existující tabulky z Google Sheetu
        vysledky_df = conn.read(worksheet="vysledky", ttl=0)
        vysledky = {str(row["id"]): {"d": row["d"], "h": row["h"], "pp_sn": bool(row["pp_sn"])} for _, row in vysledky_df.iterrows()}
    except:
        vysledky = {}

    tipy = {h: {} for h in HRACI}
    for hrac in HRACI:
        try:
            df_t = conn.read(worksheet=f"tipy_{hrac}", ttl=0)
            for _, row in df_t.iterrows():
                tipy[hrac][str(row["id"])] = {"d": row["d"], "h": row["h"]}
        except:
            pass

    zolici = {h: {} for h in HRACI}
    for hrac in HRACI:
        try:
            df_z = conn.read(worksheet=f"zolici_{hrac}", ttl=0)
            for _, row in df_z.iterrows():
                zolici[hrac][str(row["id"])] = bool(row["aktivni"])
        except:
            pass

    celkove_tipy = {}
    for hrac in HRACI:
        try:
            df_ct = conn.read(worksheet=f"celkove_{hrac}", ttl=0).iloc[0]
            celkove_tipy[hrac] = {
                "mistr": df_ct["mistr"],
                "semifinale": [df_ct["sf1"], df_ct["sf2"], df_ct["sf3"], df_ct["sf4"]],
                "cesko": df_ct["cesko"],
                "mvp": df_ct["mvp"],
                "goly": df_ct["goly"]
            }
        except:
            celkove_tipy[hrac] = {"mistr": "", "semifinale": ["", "", "", ""], "cesko": "Základní skupina", "mvp": "", "goly": 0}

    # Načtení matice statistik hráčů ČR
    try:
        df_kb = conn.read(worksheet="stats_cr", ttl=0)
        kanadske_bodovani = {}
        for _, row in df_kb.iterrows():
            hrac_jmeno = row["Hráč"]
            kanadske_bodovani[hrac_jmeno] = {}
            for col in SLOUPCE_MATICE:
                kanadske_bodovani[hrac_jmeno][col] = int(row[col])
    except:
        kanadske_bodovani = {hrac: {col: 0 for col in SLOUPCE_MATICE} for hrac in SOUPISKA_CR}

    return {"vysledky": vysledky, "tipy": tipy, "zolici": zolici, "celkove_tipy": celkove_tipy, "kanadske_bodovani": kanadske_bodovani}

def uloz_vysledky(vysledky):
    rows = [{"id": k, "d": v["d"], "h": v["h"], "pp_sn": int(v["pp_sn"])} for k, v in vysledky.items()]
    if rows:
        df = pd.DataFrame(rows)
        conn.update(worksheet="vysledky", data=df)

def uloz_tipy_hrace(hrac, hrac_tipy):
    rows = [{"id": k, "d": v["d"], "h": v["h"]} for k, v in hrac_tipy.items()]
    df = pd.DataFrame(rows if rows else [None])
    conn.update(worksheet=f"tipy_{hrac}", data=df)

def uloz_zoliky_hrace(hrac, hrac_zolici):
    rows = [{"id": k, "aktivni": int(v)} for k, v in hrac_zolici.items()]
    df = pd.DataFrame(rows if rows else [None])
    conn.update(worksheet=f"zolici_{hrac}", data=df)

def uloz_celkove_tipy_hrace(hrac, ct):
    row = {
        "mistr": ct["mistr"],
        "sf1": ct["semifinale"][0], "sf2": ct["semifinale"][1], "sf3": ct["semifinale"][2], "sf4": ct["semifinale"][3],
        "cesko": ct["cesko"], "mvp": ct["mvp"], "goly": ct["goly"]
    }
    df = pd.DataFrame([row])
    conn.update(worksheet=f"celkove_{hrac}", data=df)

def uloz_stats_cr(kb):
    rows = []
    for hrac in SOUPISKA_CR:
        r = {"Hráč": hrac}
        for col in SLOUPCE_MATICE:
            r[col] = kb[hrac].get(col, 0)
        rows.append(r)
    df = pd.DataFrame(rows)
    conn.update(worksheet="stats_cr", data=df)

# Načtení dat z tabulky
data = nacti_vsechna_data()

# --- VÝPOČET BODOVÁNÍ PRO HRÁČE ---
def spocitej_body_hrace(tip_d, tip_h, real_d, real_h, je_zolik=False):
    if tip_d is None or tip_h is None or real_d is None or real_h is None:
        return 0, False
    if tip_d == real_d and tip_h == real_h:
        body = 10
        presny = True
    else:
        presny = False
        vitez_tip = "D" if tip_d > tip_h else ("H" if tip_h > tip_d else "R")
        vitez_real = "D" if real_d > real_h else ("H" if real_h > real_d else "R")
        rozdil_tip = tip_d - tip_h
        rozdil_real = real_d - real_h
        goly_tip = tip_d + tip_h
        goly_real = real_d + real_h
        
        if (vitez_tip == vitez_real and rozdil_tip == rozdil_real) or (vitez_tip == vitez_real and goly_tip == goly_real) or (vitez_real == "R" and vitez_tip == "R"):
            body = 6
        elif vitez_tip == vitez_real:
            body = 4
        elif goly_tip == goly_real:
            body = 2
        else:
            body = 0
    if je_zolik:
        body = body * 2 if body > 0 else -2
    return body, presny

# --- DYNAMICKÝ VÝPOČET TABULEK SKUPIN MS ---
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

    sorted_a = sorted(tab_a.items(), key=lambda x: (x[1][0], x[1][1], x[1][2]), reverse=True)
    sorted_b = sorted(tab_b.items(), key=lambda x: (x[1][0], x[1][1], x[1][2]), reverse=True)
    
    return sorted_a, sorted_b, celkem_golu

# --- MATICE KANADSKÉHO BODOVÁNÍ ---
def ziskej_dataframe_statistik(data_turnaje):
    kb = data_turnaje.get("kanadske_bodovani", {})
    rows = []
    for hrac in SOUPISKA_CR:
        row = {"Hráč": hrac}
        celk_goly = 0
        celk_asist = 0
        for z in ZAPASY_TYPY:
            g = int(kb.get(hrac, {}).get(f"{z} (G)", 0))
            a = int(kb.get(hrac, {}).get(f"{z} (A)", 0))
            row[f"{z} (G)"] = g
            row[f"{z} (A)"] = a
            celk_goly += g
            celk_asist += a
        row["Celkem Góly"] = celk_goly
        row["Celkem Asistence"] = celk_asist
        row["Celkem Body (G+A)"] = celk_goly + celk_asist
        rows.append(row)
    return pd.DataFrame(rows)

def urci_nejlepsi_hrace(df):
    if df["Celkem Body (G+A)"].max() == 0:
        return "Žádná data (0+0)"
    df_sorted = df.sort_values(by=["Celkem Body (G+A)", "Celkem Góly"], ascending=[False, False])
    max_body = df_sorted.iloc[0]["Celkem Body (G+A)"]
    max_goly = df_sorted.iloc[0]["Celkem Góly"]
    top_hraci = df_sorted[(df_sorted["Celkem Body (G+A)"] == max_body) & (df_sorted["Celkem Góly"] == max_goly)]
    vystup = [f"{r['Hráč']} ({r['Celkem Body (G+A)']} b. / {r['Celkem Góly']}+{r['Celkem Asistence']})" for _, r in top_hraci.iterrows()]
    return ", ".join(vystup)

sorted_skupina_a, sorted_skupina_b, celkove_goly_ms = generuj_tabulky_ms(data)
df_statistiky = ziskej_dataframe_statistik(data)
nejlepsi_cesi_output = urci_nejlepsi_hrace(df_statistiky)

# Výpočet celkového pořadí hráčů
statistiky_hracu = {h: {"body": 0, "presne": 0} for h in HRACI}
for hrac in HRACI:
    for z in ZAPASY:
        z_id = z["id"]
        if z_id in data["vysledky"] and z_id in data["tipy"][hrac]:
            t = data["tipy"][hrac][z_id]
            r = data["vysledky"][z_id]
            zolik = data["zolici"][hrac].get(z_id, False)
            if t.get("d") is not None and r.get("d") is not None:
                b, p = spocitej_body_hrace(t["d"], t["h"], r["d"], r["h"], zolik)
                statistiky_hracu[hrac]["body"] += b
                if p: statistiky_hracu[hrac]["presne"] += 1

# --- OBRAZOVKA PŘIHLÁŠENÍ ---
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
if st.sidebar.button("Odhlásit se 🚪"):
    del st.session_state["uzivatel"]
    st.rerun()

if current_user == "admin":
    menu = ["Hlavní přehled", "Zadávání výsledků", "Správa statistik ČR (Excel matice)"]
else:
    menu = ["Hlavní přehled", "Moje tipy (Zápasy) 📝", "Celoturnajové tipy 🏆", "Tipy ostatních 👀"]
volba = st.sidebar.radio("Menu", menu)

def zobraz_tabulku_skupiny_native(sorted_data):
    rows = [{"Poř.": f"{idx+1}.", "Tým": tym, "Body": stats[0], "Skóre": f"+{stats[1]}" if stats[1] > 0 else f"{stats[1]}", "Góly": stats[2]} for idx, (tym, stats) in enumerate(sorted_data)]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=False, hide_index=True, column_config={
        "Poř.": st.column_config.TextColumn("Poř.", width="small"),
        "Tým": st.column_config.TextColumn("Tým", width="medium"),
        "Body": st.column_config.NumberColumn("Body", format="%d b.", width="small"),
        "Skóre": st.column_config.TextColumn("Skóre", width="small"),
        "Góly": st.column_config.NumberColumn("Góly", format="%d g.", width="small"),
    })

# --- 1. ZÁLOŽKA: HLAVNÍ PŘEHLED ---
if volba == "Hlavní přehled":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("🏆 Žebříček tipovačky")
        zebricek = sorted([{"jmeno": h, "body": stats["body"], "presne": stats["presne"]} for h, stats in statistiky_hracu.items()], key=lambda x: (x["body"], x["presne"]), reverse=True)
        for idx, p in enumerate(zebricek):
            medaile = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🔵"
            st.markdown(f"<div style='background-color: rgba(30,61,89,0.05); padding: 8px; border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between;'><b>{medaile} {idx+1}. {p['jmeno']}</b><span><b>{p['body']} B</b> (🎯 {p['presne']}x)</span></div>", unsafe_allow_html=True)
            
        st.write("---")
        st.subheader("📊 Statistiky MS v hokeji")
        col1, col2 = st.columns(2)
        col1.metric("Celkem gólů na MS", f"{celkove_goly_ms} 🚨")
        col2.metric("Nejlepší Čech (G+A)", f"{nejlepsi_cesi_output} 🇨🇿")
        
        with st.expander("📊 Kompletní tabulka kanadského bodování českého týmu"):
            df_divaci = df_statistiky.sort_values(by=["Celkem Body (G+A)", "Celkem Góly"], ascending=[False, False])
            st.dataframe(df_divaci[["Hráč", "Celkem Góly", "Celkem Asistence", "Celkem Body (G+A)"]], use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("📋 Živé tabulky skupin")
        tab_a, tab_b = st.tabs(["Skupina A", "Skupina B"])
        with tab_a: zobraz_tabulku_skupiny_native(sorted_skupina_a)
        with tab_b: zobraz_tabulku_skupiny_native(sorted_skupina_b)

# --- 2. ZÁLOŽKA: MOJE TIPY (ZÁPASY) ---
elif volba == "Moje tipy (Zápasy) 📝":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("📝 Tipování zápasů")
        vybrany_den = st.selectbox("Vyber hrací den:", DNY)
        
        aktivni_zolik_dnes = None
        for z in ZAPASY:
            if z["den"] == vybrany_den and data["zolici"][current_user].get(z["id"], False):
                aktivni_zolik_dnes = z["id"]

        st.write(f"### Zápasy pro: {vybrany_den}")
        for z in ZAPASY:
            if z["den"] != vybrany_den: continue
            z_id = z["id"]
            zapas_odehran = z_id in data["vysledky"]
            
            st.write(f"**{z['datum']} | {z['domaci']} vs. {z['hoste']}**")
            stary_d = data["tipy"][current_user].get(z_id, {}).get("d", 0)
            stary_h = data["tipy"][current_user].get(z_id, {}).get("h", 0)
            
            c1, c2, c3 = st.columns([1, 1, 2])
            tip_d = c1.number_input(f"Skóre {z['domaci']}", min_value=0, value=int(stary_d), key=f"d_{z_id}", disabled=zapas_odehran)
            tip_h = c2.number_input(f"Skóre {z['hoste']}", min_value=0, value=int(stary_h), key=f"h_{z_id}", disabled=zapas_odehran)
            
            je_z = (aktivni_zolik_dnes == z_id)
            zolik = c3.checkbox("💥 Žolík dne", value=je_z, key=f"z_{z_id}", disabled=zapas_odehran)
            
            data["tipy"][current_user][z_id] = {"d": tip_d, "h": tip_h}
            if zolik:
                for ost_z in ZAPASY:
                    if ost_z["den"] == vybrany_den: data["zolici"][current_user][ost_z["id"]] = False
                data["zolici"][current_user][z_id] = True
            elif aktivni_zolik_dnes == z_id and not zolik:
                data["zolici"][current_user][z_id] = False
                
        if st.button("Uložit zápis zápasů 💾"):
            uloz_tipy_hrace(current_user, data["tipy"][current_user])
            uloz_zoliky_hrace(current_user, data["zolici"][current_user])
            st.success("Tipy pro vybraný den uloženy do Google Tabulky!")
            time.sleep(0.5)
            st.rerun()

# --- 3. ZÁLOŽKA: CELOTURNAJOVÉ TIPY ---
elif volba == "Celoturnajové tipy 🏆":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("🏆 Celoturnajové bonusové tipy")
        ct = data["celkove_tipy"][current_user]
        ct["mistr"] = st.text_input("Kdo vyhraje zlato (Mistr světa)?", value=ct.get("mistr", ""))
        
        st.write("**Čtyři semifinalisté:**")
        sf1 = st.text_input("Tým 1", value=ct["semifinale"][0])
        sf2 = st.text_input("Tým 2", value=ct["semifinale"][1])
        sf3 = st.text_input("Tým 3", value=ct["semifinale"][2])
        sf4 = st.text_input("Tým 4", value=ct["semifinale"][3])
        ct["semifinale"] = [sf1, sf2, sf3, sf4]
        
        faze_list = ["Základní skupina", "Čtvrtfinále", "Semifinále", "Bronz", "Stříbro", "Zlato 🥇"]
        stary_index = faze_list.index(ct["cesko"]) if ct.get("cesko") in faze_list else 0
        ct["cesko"] = st.selectbox("Jaké fáze dosáhne český tým?", faze_list, index=stary_index)
        ct["mvp"] = st.text_input("Nejužitečnější český hráč turnaje (MVP)?", value=ct.get("mvp", ""))
        ct["goly"] = st.number_input("Celkový počet gólů v celém mistrovství?", min_value=0, value=int(ct.get("goly", 0)))
        
        if st.button("Uložit celoturnajové tipy 💾"):
            uloz_celkove_tipy_hrace(current_user, ct)
            st.success("Uloženo do Google Tabulky!")

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
                    přípona = " (PP/SN)" if data["vysledky"][z_id].get("pp_sn", False) else ""
                    st.write(f"🏁 *Výsledek:* `{data['vysledky'][z_id]['d']} : {data['vysledky'][z_id]['h']}`**{přípona}**")
                for hrac in HRACI:
                    if hrac == current_user: continue
                    t = data["tipy"][hrac].get(z_id, {"d": "-", "h": "-"})
                    zol = " 🔥" if data["zolici"][hrac].get(z_id, False) else ""
                    if odehran: st.write(f"• {hrac}: **{t['d']} : {t['h']}**{zol}")
                    else: st.write(f"• {hrac}: *? : ?* (Utajeno)")
                st.write("---")
        else:
            for hrac in HRACI:
                if hrac == current_user: continue
                with st.expander(f"Dlouhodobé tipy: {hrac}"):
                    ct = data["celkove_tipy"][hrac]
                    st.write(f"🥇 **Mistr:** {ct.get('mistr', '-')}")
                    st.write(f"🏒 **Semifinalisté:** {', '.join([x for x in ct.get('semifinale', []) if x])}")
                    st.write(f"🇨🇿 **Fáze Česka:** {ct.get('cesko', '-')}")
                    st.write(f"🎯 **Český MVP:** {ct.get('mvp', '-')}")
                    st.write(f"🚨 **Tip gólů:** {ct.get('goly', '-')}")

# --- 5. ADMIN ZÁLOŽKA: ZADÁVÁNÍ VÝSLEDKŮ ---
elif volba == "Zadávání výsledků" and current_user == "admin":
    c_l, c_main, c_r = st.columns([1, 4, 1])
    with c_main:
        st.title("👑 Administrace: Zadávání reálných výsledků")
        v_den = st.selectbox("Vyber den zápasů:", DNY)
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
            
            if odehrano: data["vysledky"][z_id] = {"d": r_d, "h": r_h, "pp_sn": pp_sn}
            else:
                if z_id in data["vysledky"]: del data["vysledky"][z_id]
            st.write("---")
            
        if st.button("Uložit zápasy a přepočítat celou aplikaci 🔄"):
            uloz_vysledky(data["vysledky"])
            st.success("Zápasy bezpečně synchronizovány s Google Sheets!")
            time.sleep(0.5)
            st.rerun()

# --- 6. ADMIN ZÁLOŽKA: EXCEL MATICE STATISTIK ČR ---
elif volba == "Správa statistik ČR (Excel matice)" and current_user == "admin":
    st.title("👑 Administrace: Kanadské bodování")
    df_editor_input = df_statistiky.drop(columns=["Celkem Góly", "Celkem Asistence", "Celkem Body (G+A)"])
    konfigurace_sloupcu = {"Hráč": st.column_config.TextColumn("Hráč", width="medium", disabled=True)}
    for col in SLOUPCE_MATICE:
        konfigurace_sloupcu[col] = st.column_config.NumberColumn(col, width="small", min_value=0, step=1)
    
    upraveny_df = st.data_editor(df_editor_input, key="excel_stats_editor", use_container_width=True, hide_index=True, column_config=konfigurace_sloupcu)
    
    if st.button("Uložit celou tabulku statistik najednou 💾"):
        nove_kb_flat = {}
        for _, row in upraveny_df.iterrows():
            jmeno_hrace = row["Hráč"]
            nove_kb_flat[jmeno_hrace] = {col: int(row[col]) for col in SLOUPCE_MATICE}
        uloz_stats_cr(nove_kb_flat)
        st.success("Statistiky hráčů zapsány online do cloudu!")
        time.sleep(0.5)
        st.rerun()
