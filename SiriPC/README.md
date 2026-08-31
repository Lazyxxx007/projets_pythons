# 🎙️ SiriPC

> **Et si mon PC gamer pouvait simplement m'écouter ?**

Ayant récemment changé de téléphone, j'ai commencé à prendre goût à l'utilisation de **Siri** au quotidien. Pouvoir lancer une action simplement en parlant est finalement assez pratique… et je me suis alors posé une question :

**Pourquoi ne pas avoir la même expérience sur mon PC ?**

J'ai donc décidé de créer **SiriPC**, un projet personnel permettant de **contrôler mon PC Windows à distance depuis mon iPhone grâce à Siri et aux Raccourcis Apple**.

L'objectif est simple : pouvoir donner une commande vocale à Siri et laisser mon PC l'exécuter automatiquement.

> 🗣️ « Siri, augmente le volume de 10 unités. »  
> 🔊 → Le volume du PC augmente.

> 🗣️ « Siri, mets la musique en pause. »  
> ⏸️ → La lecture est mise en pause.

> 🗣️ « Siri, ouvre Blender. »  
> 🎨 → Blender se lance sur le PC.

> 🗣️ « Siri, verrouille le PC. »  
> 🔒 → Windows se verrouille.

---

## 🚀 Pourquoi ce projet ?

L'idée n'était pas simplement de reproduire Siri sur Windows, mais surtout de **me faciliter l'utilisation de mon propre PC**.

Mon ordinateur étant principalement utilisé pour le gaming, le développement, Blender, le montage vidéo et différents projets personnels, je voulais pouvoir effectuer certaines actions rapidement **sans avoir à interrompre ce que je suis en train de faire**.

Ce projet m'a également permis de travailler sur plusieurs technologies en les reliant entre elles :

**iPhone → Siri → Raccourcis → HTTP → API Flask → Windows**

Une simple phrase prononcée sur mon téléphone peut donc finir par déclencher une véritable action sur mon ordinateur.

---

## ✨ Fonctionnalités

SiriPC permet actuellement de contrôler plusieurs aspects du PC :

### 🔊 Audio
- Augmenter le volume d'une valeur donnée
- Diminuer le volume d'une valeur donnée
- Régler le volume à un niveau précis
- Mettre le volume à fond
- Mettre le volume à zéro
- Couper / réactiver le son

### 💡 Affichage
- Augmenter la luminosité
- Diminuer la luminosité
- Régler la luminosité à un niveau précis
- Mettre la luminosité au maximum / minimum
- Activer / désactiver l'éclairage nocturne

### 🎵 Multimédia
- Mettre la musique en pause
- Rejouer la musique
- Passer à la musique suivante
- Revenir à la musique précédente

### 🟦 Système
- Activer / désactiver le Bluetooth
- Verrouiller le PC
- Éteindre le PC
- Redémarrer le PC

### 🚀 Applications
Lancer rapidement des applications et services depuis Siri, notamment :

- 🎵 Spotify
- 💬 Discord
- 🎮 Steam
- 🌐 Google Chrome
- 🌐 Brave
- 🎨 Blender
- 🎬 Adobe After Effects
- 🎞️ Adobe Media Encoder
- ⚙️ Armoury Crate
- 📺 Netflix
- 📺 Prime Video

---

## 🧠 Architecture

```text
             📱 iPhone
                 │
               Siri
                 │
          Apple Raccourcis
                 │
               HTTP
                 │
                 ▼
        🖥️ PC Windows
                 │
             Flask API
                 │
        ┌────────┴────────┐
        ▼                 ▼
    pycaw / Windows    PyAutoGUI
        │                 │
        ▼                 ▼
     🔊 Audio       🎵 Multimédia
     💡 Affichage
     🟦 Bluetooth
     🚀 Applications
```

---

## 🛠️ Technologies utilisées

- **Python**
- **Flask** — création de l'API HTTP
- **pycaw** — contrôle du volume Windows
- **PyAutoGUI** — contrôle de certaines fonctions multimédia
- **comtypes** — interaction avec les composants Windows
- **screen-brightness-control** — gestion de la luminosité
- **Siri**
- **Apple Raccourcis**
- **HTTP / API REST**
- **Windows**

---

## 📁 Structure du projet

```text
SiriPC/
├── server.py
├── requirements.txt
├── .gitignore
├── .env.example
└── key.env              # 🔐 local uniquement, non versionné
```

> `key.env` contient la clé utilisée pour authentifier les requêtes.  
> Il est volontairement exclu du dépôt Git grâce au `.gitignore`.

---

## ⚙️ Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Lazyxxx007/projets_pythons.git
cd projets_pythons/SiriPC
```

### 2. Installer les dépendances

```bash
py -m pip install -r requirements.txt
```

### 3. Configurer la clé secrète

Créer un fichier :

```text
key.env
```

avec :

```env
SIRI_PC_KEY=VOTRE_CLE_SECRETE
```

⚠️ Ne partagez jamais cette clé et ne la committez jamais sur GitHub.

### 4. Lancer le serveur

```bash
py server.py
```

Le serveur écoute sur :

```text
http://0.0.0.0:5000
```

---

## 📱 Utilisation avec Siri

Le principe est de créer un **Raccourci Apple** sur l'iPhone qui envoie une requête HTTP vers l'adresse IP locale du PC.

Exemple :

```text
Siri
 ↓
Raccourci
 ↓
Requête HTTP GET
 ↓
http://IP_DU_PC:5000/command
 ↓
Commande exécutée sur Windows
```

Pour les commandes vocales plus complexes, le raccourci transmet le texte reconnu par Siri au serveur.

---

## 🔐 Sécurité

SiriPC utilise une clé secrète pour autoriser les requêtes.

La clé est chargée depuis `key.env` et **n'est pas stockée directement dans `server.py`**.

Le fichier `key.env` est également exclu de Git :

```gitignore
key.env
```

Cela permet de publier le projet sans exposer la clé personnelle utilisée par le serveur.

> ⚠️ Le serveur étant conçu pour fonctionner sur un réseau local, il est recommandé de ne pas exposer directement le port `5000` sur Internet sans ajouter des mesures de sécurité supplémentaires.

---

## 🎮 Prochaine étape : les jeux

L'une des prochaines évolutions du projet sera de pouvoir lancer directement mes jeux depuis Siri.

Par exemple :

> 🎮 « Siri, lance GTA V. »

> 🎮 « Siri, lance Dark Souls. »

> 🎮 « Siri, lance Stellar Blade. »

> 🎮 « Siri, lance Naruto. »

> 🎮 « Siri, lance Pragmata. »

L'idée serait de créer un système permettant d'associer chaque jeu à son exécutable ou à son launcher, puis de pouvoir simplement demander à Siri de le lancer.

---

## ⚠️ Contraintes actuelles : reconnaissance vocale de Siri

Le projet est encore en développement et je rencontre actuellement une contrainte qui ne vient pas directement du serveur, mais de la **reconnaissance vocale de Siri**.

Dans certaines situations, Siri ne transmet pas l'intégralité de la phrase dictée au raccourci. Certains mots ou certaines parties de la commande peuvent être coupés avant même d'arriver jusqu'à SiriPC.

Par exemple :

> 🗣️ « Diminue le volume. »

Siri peut ne pas transmettre correctement le mot **« diminue »**, ce qui empêche le serveur d'identifier la commande.

Le même problème peut apparaître avec les valeurs numériques :

> 🗣️ « Augmente le volume de 10. »

Le **« 10 »** peut ne pas être transmis correctement.

Pour contourner temporairement ce problème, je dois actuellement utiliser une formulation plus explicite :

> 🗣️ « Augmente le volume de 10 unités. »

Cette formulation est mieux reconnue dans mon cas et permet au serveur de récupérer correctement la valeur.

Je cherche actuellement une **parade permettant de rendre les commandes vocales plus naturelles et plus robustes**, sans devoir utiliser des formulations spécifiques uniquement pour contourner les limites de reconnaissance de Siri.

Cela fait donc partie des problèmes encore en cours d'expérimentation et constitue l'une des prochaines améliorations importantes du projet.

## 🔮 Évolutions possibles

Le projet pourrait ensuite évoluer vers :

- 🎮 lancement de jeux
- 🖥️ contrôle plus avancé de Windows
- 📂 ouverture de fichiers et dossiers
- 🌐 ouverture de sites web
- 🔔 notifications sur l'iPhone
- 📊 retour d'état du PC vers le raccourci
- 🤖 interprétation plus naturelle des commandes
- 🧩 commandes personnalisables
- 🔒 authentification renforcée
- 📡 contrôle depuis l'extérieur du réseau local

---

## 💭 Une idée toute simple devenue un projet

À la base, l'idée était simplement :

> **« J'utilise beaucoup Siri sur mon nouveau téléphone… pourquoi pas l'utiliser pour mon PC ? »**

Quelques expérimentations plus tard, cette petite idée est devenue un véritable projet Python permettant de **transformer des commandes vocales en actions concrètes sur mon PC gamer**.

Et finalement, c'est exactement le genre de projet personnel que j'aime : **partir d'une idée du quotidien et construire moi-même la solution.**

---

## 📌 Statut

🟢 **Projet personnel — en développement**

Le projet évolue progressivement et de nouvelles commandes seront ajoutées au fur et à mesure.

---

## 👤 Auteur

**Lazyxxx007**

Projet personnel réalisé pour expérimenter l'automatisation, Python, les API HTTP et l'intégration entre iPhone/Siri et Windows.
