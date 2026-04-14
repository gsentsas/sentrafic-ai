# SEN TRAFIC AI — État du projet
> Dernière mise à jour : 14 avril 2026

---

## ✅ FAIT (Done)

### Infrastructure & DevOps
- [x] **Docker Compose** complet — 5 services orchestrés : `postgres`, `redis`, `backend-api`, `vision-engine`, `dashboard`
- [x] **`.dockerignore`** sur chaque service (build context réduit de ~207 MB)
- [x] **Alembic migration** `0001_initial_schema.py` — tous les modèles versionnés avec enums PostgreSQL natifs
- [x] **Fallback SQLAlchemy** au démarrage si Alembic échoue (base vide au premier run)
- [x] **Healthchecks** Docker sur postgres, redis, backend (curl sur `/health`)
- [x] **`platform: linux/amd64` retiré** du backend — builds natifs ARM64 sur Apple Silicon
- [x] **Variables d'environnement** cohérentes entre services (`.env`, `.env.example`)

### Backend API (FastAPI + PostgreSQL)
- [x] **6 modèles SQLAlchemy** : `User`, `Site`, `Camera`, `TrafficAggregate`, `Alert`, `CameraHealthCheck`
- [x] **9 routers FastAPI** : auth, health, sites, cameras, dashboard, analytics, alerts, ingest, exports
- [x] **Authentification JWT** (login, token, rôles : admin / operator / viewer)
- [x] **Auth X-API-Key** sur la route d'ingest (`/api/ingest/events`) — clé partagée avec le vision-engine
- [x] **Route `/api/dashboard/overview`** — KPIs, tendance 24h, watchlist, alertes critiques
- [x] **Route `/api/cameras/{id}/traffic`** — trend, summary, distribution, alertes récentes, dernière lecture
- [x] **Correction date parsing** sur `/api/analytics/traffic` — `Optional[date]` + convertisseur `_to_datetime()` (résout le 422)
- [x] **Paramètre `granularity`** accepté sur analytics (ignoré côté backend, compatibilité frontend)
- [x] **Seed données démo** au démarrage — 4 sites Dakar, 9 caméras, ~1150 agrégats 48h, 10 alertes

### Vision Engine (Python)
- [x] **Mode démo** (`VISION_DEMO_MODE=true`) — aucune caméra physique ni YOLO requis
- [x] **Simulation trafic Dakar** — mix réaliste (50% voitures, 20% motos, 12% bus, 8% camions, 10% piétons), facteurs horaires avec pointes 7-9h et 17-19h
- [x] **Auto-seed caméras** — si la base est vide, crée automatiquement 3 sites + 4 caméras via l'API REST
- [x] **Fetch caméras actives** toutes les 10 ticks (URL corrigée avec slash final `/api/cameras/`)
- [x] **Publication toutes les 5s** → `POST /api/ingest/events` avec header `X-API-Key`
- [x] **Fix `stream.py`** — `Tuple[bool, Optional]` → `Tuple[bool, Optional[Any]]` (Python 3.11)
- [x] **Fix module path** — `python -m app.main` + `ENV PYTHONPATH=/app` (résout `ModuleNotFoundError`)
- [x] **Graceful shutdown** sur SIGTERM/SIGINT

### Dashboard (Next.js 14 + TypeScript)
- [x] **App Router** avec 8 pages : overview, cameras, cameras/[id], sites, alerts, analytics, live, settings, login
- [x] **Page `/overview`** — KPI cards, line chart 24h, alertes critiques, watchlist caméras
- [x] **Page `/cameras`** — table cliquable avec navigation vers le détail caméra
- [x] **Page `/cameras/[id]`** — KPI temps réel, trend chart, pie chart distribution, tableau par classe, alertes récentes, refresh auto 30s
- [x] **Page `/analytics`** — sélecteur de dates, filtrage par caméra, graphe trafic, distribution
- [x] **Page `/alerts`** — table filtrée par sévérité / statut résolution
- [x] **Page `/sites`** — liste des sites avec comptage caméras
- [x] **Authentification frontend** — JWT stocké en localStorage, guard de routes
- [x] **`next.config.js` corrigé** — `output: 'standalone'` et `swcMinify` retirés (résolvait le crash exit code 0)
- [x] **`package.json`** — script `dev` avec `-H 0.0.0.0 -p 3000` pour binding Docker correct
- [x] **`NEXT_TELEMETRY_DISABLED=1`** — suppression du prompt telemetry au démarrage
- [x] **Slashes finaux** — tous les appels `api.ts` utilisent `/api/cameras/` etc. (supprime les 307 redirects)

---

## 🔲 À FAIRE (Todo)

### Priorité haute — Fonctionnel MVP

- [ ] **Page Live** (`/live`) — actuellement placeholder ; brancher un flux MJPEG ou WebSocket pour afficher les frames caméra en temps réel
- [ ] **Page Settings** (`/settings`) — gestion des utilisateurs (créer / désactiver), changement de mot de passe
- [ ] **Résolution d'alertes côté UI** — bouton "Résoudre" dans la table des alertes (`POST /api/alerts/{id}/resolve`)
- [ ] **Création de site / caméra depuis le dashboard** — formulaires avec validation (les endpoints backend existent déjà)
- [ ] **Export CSV fonctionnel** — le bouton "Exporter" sur la page analytics doit appeler `GET /api/exports/traffic.csv`

### Priorité haute — Qualité & Robustesse

- [ ] **Tests backend** — les fichiers `tests/` existent mais les tests sont incomplets ; couvrir au minimum : ingest, analytics, auth, dashboard/overview
- [ ] **Gestion d'erreurs UI** — les `ErrorState` affichent le message brut de l'API ; améliorer avec messages utilisateur en français
- [ ] **Refresh token** — le JWT expire, il n'y a pas de mécanisme de renouvellement silencieux (l'utilisateur est redirigé vers `/login` brutalement)
- [ ] **`VISION_CAMERA_ID`** dans docker-compose pointe encore sur `1` (non-UUID) — supprimer cette variable ou la remplacer par un vrai UUID de caméra seed

### Priorité moyenne — Démo & Présentation

- [ ] **Page `/live`** — même en mode démo, afficher un flux simulé (grille de tiles avec stats temps réel par caméra sans vidéo)
- [ ] **Indicateur "LIVE"** sur le dashboard — badge vert animé pour signaler que des données arrivent en temps réel
- [ ] **Graphe analytics** — afficher les données de la dernière heure en premier (UX améliorée : zoom sur le présent)
- [ ] **Internationalisation dates** — les timestamps sont en UTC, les afficher en heure de Dakar (UTC+0 en hiver, UTC+1 en été)

### Priorité moyenne — Infrastructure

- [ ] **Nginx reverse proxy** — pour la production, router `/` vers le dashboard (3000) et `/api` vers le backend (8000) sur un même domaine
- [ ] **Configuration production** — `.env.production` avec JWT_SECRET fort, désactiver `APP_DEBUG`, restreindre `CORS_ORIGINS`
- [ ] **Rotation des logs** — le backend écrit dans `logs/app.log` sans rotation ; configurer `logging.handlers.RotatingFileHandler`
- [ ] **Alertes automatiques** — le service `alert_service.py` a la logique, mais il n'y a pas de job qui tourne périodiquement pour détecter les seuils de congestion → créer un worker ou un endpoint déclenché par l'ingest

### Priorité basse — Vision Engine réel

- [ ] **Intégration YOLOv8** — mode non-démo : téléchargement automatique du modèle `yolov8n.pt`, pipeline de détection complet
- [ ] **Support flux RTSP** — tester avec une vraie caméra IP ou un stream de test (ex. Big Buck Bunny en RTSP)
- [ ] **Zones de comptage** — `zones.py` existe mais n'est pas branché dans le pipeline démo ; implémenter les lignes de comptage virtuelles
- [ ] **ByteTrack tracking** — `tracker.py` existe, intégrer dans le pipeline de détection réel

### Priorité basse — Évolutions futures (roadmap v1.1+)

- [ ] **API mobile** — endpoints allégés pour une future app mobile
- [ ] **WebSocket** pour les mises à jour temps réel sans polling (remplacer le `setInterval` du dashboard)
- [ ] **Multi-tenant** — isolation des données par organisation (pour déploiement multi-villes)
- [ ] **Prédiction trafic** — modèle ML sur les données historiques (roadmap v2.0)
- [ ] **Carte interactive** — afficher les sites et caméras sur une carte Dakar (Leaflet / Mapbox)

---

## État des services au 14 avril 2026

| Service | Status | Notes |
|---------|--------|-------|
| `sentrafic-postgres` | ✅ Opérationnel | Données persistées dans volume Docker |
| `sentrafic-redis` | ✅ Opérationnel | Cache LRU 256 MB |
| `sentrafic-backend` | ✅ Opérationnel | uvicorn, 9 routers actifs, seed OK |
| `sentrafic-vision` | ✅ Opérationnel | Mode démo, 9 caméras simulées, 5s/tick |
| `sentrafic-dashboard` | ✅ Opérationnel | next dev sur :3001 |

**Commande de démarrage :**
```bash
docker compose up
```

**Accès :**
- Dashboard : http://localhost:3001
- API docs (Swagger) : http://localhost:8000/docs
- Login : `admin@sentrafic.sn` / `admin123`
