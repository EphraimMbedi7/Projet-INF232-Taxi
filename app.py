import streamlit as st
import sqlite3
import pandas as pd

# Connexion et mise à jour de la structure de la base
conn = sqlite3.connect('tarifs_taxi.db')
c = conn.cursor()
# On crée la table avec 'depart' et 'arrivee'
c.execute('''CREATE TABLE IF NOT EXISTS releves 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              depart TEXT, 
              arrivee TEXT, 
              prix INTEGER, 
              moment TEXT,
              date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

st.set_page_config(page_title="Projet INF232 - Taxi", page_icon="🚖")
st.title("🚖 Analyse des Trajets de Taxi")

# Liste des quartiers de Yaoundé
liste_quartiers = ["Melen", "Bastos", "Mvan", "Etoudi", "Olembe", "Poste Centrale", "Ngoa-Ekelle", "Madagascar", "Mokolo", "jouvence", "Nouvelle Route Tam-Tam", "Simbock","Mendong", "acacia", "byem-Assi", "Omnisport", "Emana", "Obili", "Messassi", "chell Simeyon", "Damas", "Odza", "Ekie", "Olezoa", "Kennedy","R.P express", "nkoabang", "Mballa 2", "R.P Lonkak", "Eleveur", "Nkolbisson", "Nvollye", "Efoulan", "Bonas", "Etoug-Ebe"]

# Zone de saisie
with st.form("form_saisie", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        depart = st.selectbox("Quartier de départ :", liste_quartiers)
    with col2:
        arrivee = st.selectbox("Quartier d'arrivée :", liste_quartiers)
    
    col3, col4 = st.columns(2)
    with col3:
        prix = st.number_input("Prix (FCFA) :", min_value=100, step=50, value=250)
    with col4:
        moment = st.radio("Moment :", ["Jour", "Nuit"], horizontal=True)
    
    valider = st.form_submit_button("Enregistrer le trajet")

if valider:
    c.execute("INSERT INTO releves (depart, arrivee, prix, moment) VALUES (?, ?, ?, ?)", 
              (depart, arrivee, prix, moment))
    conn.commit()
    st.toast(f"Enregistré : {depart} ➔ {arrivee}")

# Récupération des données
df = pd.read_sql_query("SELECT depart, arrivee, prix, moment, date FROM releves", conn)
# 1. On récupère les données avec l'ID (très important pour l'UPDATE)
df = pd.read_sql_query("SELECT id, depart, arrivee, prix, moment, date FROM releves", conn)

if not df.empty:
    st.metric("Total des trajets collectés", len(df))
    st.metric("Prix moyen d'un trajet", f"{round(df['prix'].mean(), 2)} FCFA")
    
    st.subheader("📝 Correction des erreurs")
    st.info("Double-cliquez sur une case pour modifier, puis cliquez sur 'Enregistrer'.")
    
    # 2. On affiche le tableau interactif
    # On utilise hide_index=True pour que ce soit plus joli
    edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
    
    # 3. Le bouton qui valide les changements vers SQLite
    if st.button("💾 Enregistrer les modifications"):
        for index, row in edited_df.iterrows():
            c.execute("""UPDATE releves SET depart=?, arrivee=?, prix=?, moment=? WHERE id=?""", 
                      (row['depart'], row['arrivee'], row['prix'], row['moment'], row['id']))
        conn.commit()
        st.success("Modifications enregistrées !")
        st.rerun()
if not df.empty:
    st.metric("Total des trajets collectés", len(df))
    
    # Création d'une colonne "Trajet" pour le graphique
    df['Trajet'] = df['depart'] + " ➔ " + df['arrivee']
    
    tab1, tab2 = st.tabs(["📊 Graphique par Trajet", "📋 Données Brutes"])
    
    with tab1:
        df_moyen = df.groupby(['Trajet', 'moment'])['prix'].mean().reset_index()
        st.bar_chart(data=df_moyen, x='Trajet', y='prix', color='moment')
    
    with tab2:
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)

    st.divider()
st.subheader("🛠️ Gestion des erreurs")
if not df.empty:
    # Créer une liste d'IDs pour choisir quoi supprimer
    id_a_supprimer = st.selectbox("Sélectionner l'ID du trajet à corriger :", df.index)

conn.close()