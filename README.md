# 🎵 Discord Music Bot (Slash Commands)

Un bot Discord simple et puissant pour lire de la musique depuis YouTube avec commandes slash.

## 🚀 Fonctionnalités

- 🔊 Lecture de musique depuis YouTube
- 📄 Commandes Slash intuitives (`/play`, `/skip`, `/pause`, etc.)
- 🎶 File d'attente par serveur
- 🎨 Affichage des titres, miniatures, durées et demandeurs
- 🧼 Téléchargement temporaire (pas de streaming instable)

## 🛠️ Technologies utilisées

- [discord.py 2.x](https://discordpy.readthedocs.io/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)
- [PyNaCl](https://pypi.org/project/PyNaCl/)

---

## 📦 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/music-bot.git
cd music-bot
````

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

> Exemple de `requirements.txt` :
>
> ```txt
> discord.py>=2.3
> yt-dlp
> PyNaCl
> ```

### 3. Installer FFmpeg

* Linux : `sudo apt install ffmpeg`
* Windows : [Téléchargez ici](https://ffmpeg.org/download.html) et ajoutez le binaire à votre PATH

---

## 🔧 Configuration

Dans le fichier `bot.py`, remplacez la ligne suivante :

```python
TOKEN = 'VOTRE_TOKEN_DISCORD_ICI'
```

Par votre token Discord (disponible depuis le [portail développeur Discord](https://discord.com/developers/applications)).

---

## ▶️ Lancer le bot

```bash
python bot.py
```

---

## 🧪 Commandes disponibles

| Slash Commande | Description                                                    |
| -------------- | -------------------------------------------------------------- |
| `/join`        | Connecte le bot à votre canal vocal                            |
| `/leave`       | Déconnecte le bot du canal                                     |
| `/play`        | Joue une musique à partir d'une URL ou d'une recherche YouTube |
| `/skip`        | Passe à la musique suivante                                    |
| `/pause`       | Met en pause la musique                                        |
| `/resume`      | Reprend la musique                                             |
| `/stop`        | Arrête la lecture et vide la file                              |
| `/now`         | Affiche la chanson en cours                                    |

---

## ❓ FAQ

**Q : Pourquoi le bot coupe la musique après quelques secondes ?**
R : Ce problème a été corrigé en désactivant le streaming direct. Le bot télécharge temporairement les fichiers pour plus de stabilité.

**Q : Puis-je héberger ce bot sur Replit/Heroku/Docker ?**
R : Oui, tant que `ffmpeg` est installé et accessible via le PATH.

---

## 🧑‍💻 Contribution

Les contributions sont les bienvenues ! Forkez ce dépôt, ouvrez une *pull request* ou signalez un problème dans les issues.


