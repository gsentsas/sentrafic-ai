# SEN TRAFIC AI — État du projet
> Dernière mise à jour : 15 avril 2026

---

## ✅ FAIT (Done)

### Infrastructure & DevOps
- [x] **Docker Compose** complet — 5 services orchestrés : `postgres`, `redis`, `backend-api`, `vision-engine`, `dashboard`
- [x] **`.dockerignore`** sur chaque service (build context réduit de ~207 MB)
- [x] **Alembic migration** `0001_initial_schema.py` — tous les modèles versionnés avec enums PostgreSQL natifs
- [x] **Fallback SQLAlchemy** au démarrage si Alembic échoue
- [x] **Healthchecks** Docker sur postgres, redis, backend
- [x] **`platform: linux/amd64` retiré** — builds natifs ARM64 sur Apple Silicon
- [x] **`VISION_CAMERA_ID: 1`** supprimé du docker-compose (n'était pas un UUID valide)
- [x] **Variables d'environnement** cohérentes (`.env`, `.env.example`)

### Backend API (FastAPI + PostgreSQL)
- [x] **6 modèles SQLAlchemy** : `User`, `Site`, `Camera`, `TrafficAggregate`, `Alert`, `CameraHealthCheck`
- [x] **10 routers FastAPI** : auth, health, sites, cameras, dashboard, analytics, alerts, ingest, exports, users
- [x] **Authentification JWT** (login, token, rôles : admin / operator / viewer)
- [x] **Auth X-API-Key** sur la route d'ingest
- [x] **Router `/api/users`** — `GET /me`, `PUT /me/password`, `GET /` (admin), `POST /` (admin), `PUT /{id}` (admin)
- [x] **Route `/api/dashboard/overview`** — KPIs, tendance 24h, watchlist, alertes
- [x] **Route `/api/cameras/{id}/traffic`** — trend, summary, distribution, alertes, dernière lecture
- [x] **Correction date parsing** — `Optional[date]` + `_to_datetime()` sur analytics et exports (résout le 422)
- [x] **Export CSV** — `GET /api/exports/traffic.csv` avec filtres
- [x] **Fix route resolve alert** — retour dict corrigé
- [x] **`get_current_user`** utilise la DI FastAPI + conversion UUID string→UUID
- [x] **Seed données démo** — 4 sites Dakar, 9 caméras, ~1150 agrégats 48h, 10 alertes

### Vision Engine (Python)
- [x] **Mode démo** (`VISION_DEMO_MODE=true`) — sans caméra physique ni YOLO
- [x] **Simulation trafic Dakar** — mix réaliste, facteurs horaires (pointes 7-9h et 17-19h)
- [x] **Auto-authentification** — le pipeline s'authentifie via JWT pour accéder aux routes protégées
- [x] **Auto-seed caméras** — crée sites + caméras Dakar via l'API REST si base vide
- [x] **Publication toutes les 5s** → `POST /api/ingest/events` avec `X-API-Key`
- [x] **Fix `stream.py`** — `Tuple[bool, Optional[Any]]` (Python 3.11)
- [x] **Fix module path** — `python -m app.main` + `ENV PYTHONPATH=/app`
- [x] **Modèle YOLO** `yolov8n.pt` présent dans le repo (6.5 MB)
- [x] **Vidéo démo** `samples/videos/demo.mp4` présente (12 MB)
- [x] **Graceful shutdown** sur SIGTERM/SIGINT

### Dashboard (Next.js 14 + TypeScript) — 9 pages
- [x] **Lib files pushés** : `api.ts`, `auth.ts`, `constants.ts`, `format.ts`, `types.ts`
- [x] **Page `/overview`** — KPI cards, line chart 24h, alertes critiques, watchlist
- [x] **Page `/cameras`** — table cliquable, formulaire de création, toggle actif/inactif inline
- [x] **Page `/cameras/[id]`** — KPI temps réel, charts, alertes, refresh auto 30s
- [x] **Page `/sites`** — liste + formulaire de création avec validation, filtre par type
- [x] **Page `/sites/[id]`** — détail site avec liste des caméras associées
- [x] **Page `/alerts`** — filtres (sévérité / statut), bouton Résoudre branché et fonctionnel
- [x] **Page `/analytics`** — graphes, export CSV réel avec téléchargement navigateur
- [x] **Page `/live`** — grille temps réel (actives / inactives), badge LIVE/PÉRIMÉ, barres distribution, occupancy ; refactorisée en composant client (`live-page-client.tsx`) pour compatibilité App Router
- [x] **Page `/settings`** — profil, changement mot de passe, gestion utilisateurs (admin)
- [x] **Authentification frontend** — JWT localStorage, guard de routes
- [x] **Composant `Modal`** — overlay réutilisable (ESC + backdrop click)
- [x] **`LiveCameraTile`** — fetch trafic individuel, badge LIVE animé, badge PÉRIMÉ, `trafficSnapshot` prop, `selected` / `onToggleLive` pour mur live
- [x] **`CamerasTable`** — toggle actif/inactif inline (switch animé)
- [x] **Hook `use-live-summary`** — polling adaptatif avec compteur d'échecs consécutifs
- [x] **Messages d'erreur en français** — `LoadingState`, `ErrorState`
- [x] **Slashes finaux** — tous les appels `api.ts` (plus de 307 redirects)
- [x] **`NEXT_TELEMETRY_DISABLED=1`** dans docker-compose

### Tests backend (41/43 passent)
- [x] `test_auth.py` — 10 tests (login, /me, users CRUD, changement mot de passe)
- [x] `test_ingest.py` — 6 tests (clé API, batch, congestion → alerte, statut caméra)
- [x] `test_dashboard.py` — 7 tests (structure, comptages, analytics, resolve alert)
- [x] `test_sites.py` — CRUD sites
- [x] `test_camera_traffic_route.py` — route trafic caméra
- [x] `test_authz_protected_routes.py` — routes protégées (401 sans token)
- [x] `test_health.py` — santé système
- [x] **Conftest** — patch SQLite UUID, fixtures `ingest_client`, `admin_client`

---

## 🔲 À FAIRE (Todo)

### Corrections immédiates (2 tests en échec)
- [ ] **`test_dashboard_live_summary`** — endpoint `/api/dashboard/live-summary` non exposé dans le router (`__init__.py`)
- [ ] **`test_api_health_check`** — format de réponse du test ne correspond pas à l'implémentation actuelle de `/api/health/`

### Priorité haute — Fonctionnel démo
- [ ] **Page `/live` — mur live** — la tile a `selected` + `onToggleLive` mais la page ne gère pas encore l'état multi-sélection
- [ ] **Hook `use-live-summary`** — brancher le polling adaptatif sur la page `/live`
- [ ] **Refresh token JWT** — pas de renouvellement silencieux → l'utilisateur est redirigé `/login` à l'expiration
- [ ] **Export CSV filtre site_id** — l'UI analytics n'expose pas encore de filtre par site

### Priorité moyenne — UX & Infrastructure
- [ ] **Page `/sites/[id]`** — formulaire d'édition (le détail est lisible, pas encore modifiable)
- [ ] **Carte interactive** — sites Dakar sur Leaflet / OpenStreetMap
- [ ] **Nginx reverse proxy** — pour un déploiement production sur un seul domaine
- [ ] **`.env.production`** — JWT_SECRET fort, `APP_DEBUG=false`, CORS restrictif
- [ ] **Alertes automatiques** — détection de seuil à l'ingest (logique prête, pas de job périodique)
- [ ] **Rotation des logs** backend (`RotatingFileHandler`)
- [ ] **Internationalisation dates** — afficher en heure de Dakar (UTC+0)

### Priorité basse — Vision Engine réel
- [ ] **Pipeline YOLO complet** — `yolov8n.pt` est présent, brancher la détection temps réel
- [ ] **Support flux RTSP** — tester avec `demo.mp4` puis une vraie caméra IP
- [ ] **Zones de comptage** — `zones.py` + `counters.py` existants, non branchés dans le pipeline
- [ ] **ByteTrack tracking** — `tracker.py` existant, non intégré

### Évolutions futures (roadmap v1.1+)
- [ ] **WebSocket** — temps réel sans polling
- [ ] **API mobile** — endpoints allégés
- [ ] **Multi-tenant** — isolation par organisation
- [ ] **Prédiction trafic** — ML sur données historiques (roadmap v2.0)

---

## État des services — 15 avril 2026

| Service | Status | Notes |
|---------|--------|-------|
| `sentrafic-postgres` | ✅ Opérationnel | Données persistées |
| `sentrafic-redis` | ✅ Opérationnel | Cache LRU 256 MB |
| `sentrafic-backend` | ✅ Opérationnel | 10 routers, seed OK, 41/43 tests |
| `sentrafic-vision` | ✅ Opérationnel | Auth JWT, 9 caméras, 5s/tick |
| `sentrafic-dashboard` | ✅ Opérationnel | next dev sur :3001, 9 pages |

## Commits pushés

| Hash | Message |
|------|---------|
| `5937e1f` | Make live page dynamic in Next app router |
| `106c2a7` | Add missing dashboard lib files (api, auth, constants, format, types) |
| `bc9003f` | Add vision engine venv artifacts |
| `2244123` | Add backend models package required for production runtime |
| `e753bfd` | Add full WIP consolidation across backend, dashboard, docs, vision engine |
| `d0e6166` | Stabilize live monitoring workflow and site navigation for Sprint 1 |
| `1145ba7` | MVP initial generation - baseline for consolidation pass |

## Commande de démarrage
```bash
docker compose up
```

## Accès démo
| URL | Description |
|-----|-------------|
| http://localhost:3001 | Dashboard |
| http://localhost:8000/docs | Swagger API |

**Identifiants :**
- Admin : `admin@sentrafic.sn` / `admin123`
- Opérateur : `operateur@sentrafic.sn` / `operateur123`
- Observateur : `observateur@sentrafic.sn` / `observateur123`
