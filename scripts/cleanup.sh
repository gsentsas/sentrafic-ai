#!/usr/bin/env bash
# ============================================================
# SEN TRAFIC AI - Script de nettoyage systeme intelligent
# Usage: chmod +x scripts/cleanup.sh && ./scripts/cleanup.sh
# Debug: PS4='+ ligne ${LINENO}: ' bash -x ./scripts/cleanup.sh
# ============================================================

set -uE -o pipefail
shopt -s nullglob

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${CYAN}[i]${NC} $1"; }
err()  { echo -e "${RED}[X]${NC} $1"; }

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

bytes_to_human() {
  local bytes="${1:-0}"
  if   (( bytes >= 1073741824 )); then echo "$(( bytes / 1073741824 )) Go"
  elif (( bytes >= 1048576 ));    then echo "$(( bytes / 1048576 )) Mo"
  elif (( bytes >= 1024 ));       then echo "$(( bytes / 1024 )) Ko"
  else echo "${bytes} o"
  fi
}

get_avail_kb() {
  df -k / 2>/dev/null | awk 'NR==2 {print $4+0}'
}

dir_size_mb() {
  local dir="$1"
  [ -d "$dir" ] || { echo 0; return; }
  du -sm "$dir" 2>/dev/null | awk '{print $1+0}'
}

sudo_ready() {
  sudo -n true >/dev/null 2>&1
}

# Timeout portable pour eviter les blocages Docker sur macOS
run_with_timeout() {
  local seconds="$1"
  shift

  (
    "$@"
  ) &
  local cmd_pid=$!

  (
    sleep "$seconds"
    kill -TERM "$cmd_pid" >/dev/null 2>&1 || true
    sleep 1
    kill -KILL "$cmd_pid" >/dev/null 2>&1 || true
  ) &
  local timer_pid=$!

  wait "$cmd_pid" >/dev/null 2>&1
  local status=$?

  kill -TERM "$timer_pid" >/dev/null 2>&1 || true
  wait "$timer_pid" >/dev/null 2>&1 || true

  return "$status"
}

docker_cli_exists() {
  command_exists docker
}

docker_ready() {
  docker_cli_exists || return 1
  run_with_timeout 4 docker info >/dev/null 2>&1
}

echo ""
echo "=========================================="
echo "  SEN TRAFIC AI - Nettoyage systeme"
echo "=========================================="
echo ""

OS="$(uname -s)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

info "Projet detecte: $PROJECT_DIR"
info "Systeme detecte: $OS"
echo ""

# ============================================================
# 0. ETAT DISQUE AVANT
# ============================================================
echo "── 0. Etat du disque avant nettoyage ──"
info "Espace disque avant nettoyage:"
df -h / 2>/dev/null | tail -1
BEFORE_AVAIL="$(get_avail_kb)"
echo ""

# ============================================================
# 1. DOCKER
# ============================================================
echo "── 1. Docker ──"

if docker_cli_exists; then
  if docker_ready; then
    RUNNING="$(docker ps -q 2>/dev/null | wc -l | tr -d ' ')"
    if (( RUNNING > 0 )); then
      info "$RUNNING conteneur(s) en cours d'execution"
      docker ps --format "  - {{.Names}} ({{.Image}}) up {{.Status}}" 2>/dev/null || true
      echo ""
      info "Arret des conteneurs en cours..."
      docker stop $(docker ps -q) >/dev/null 2>&1 || true
      log "Conteneurs arretes"
    else
      log "Aucun conteneur en cours d'execution"
    fi

    info "Nettoyage Docker..."

    STOPPED="$(docker ps -a -q --filter "status=exited" 2>/dev/null | wc -l | tr -d ' ')"
    if (( STOPPED > 0 )); then
      info "Suppression de $STOPPED conteneur(s) arretes..."
      docker container prune -f >/dev/null 2>&1 || true
    fi

    DANGLING="$(docker images -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')"
    if (( DANGLING > 0 )); then
      info "Suppression de $DANGLING image(s) pendante(s)..."
      docker image prune -f >/dev/null 2>&1 || true
    fi

    UNUSED_IMAGES="$(docker images -q 2>/dev/null | wc -l | tr -d ' ')"
    if (( UNUSED_IMAGES > 3 )); then
      info "Suppression des images Docker non utilisees..."
      docker image prune -a -f >/dev/null 2>&1 || true
    fi

    DANGLING_VOLUMES="$(docker volume ls -q -f "dangling=true" 2>/dev/null | wc -l | tr -d ' ')"
    if (( DANGLING_VOLUMES > 0 )); then
      info "Suppression de $DANGLING_VOLUMES volume(s) orphelin(s)..."
      docker volume prune -f >/dev/null 2>&1 || true
    fi

    info "Nettoyage des networks inutilises..."
    docker network prune -f >/dev/null 2>&1 || true

    info "Nettoyage du build cache Docker..."
    docker builder prune -f >/dev/null 2>&1 || true

    log "Docker nettoye"
  else
    warn "Docker installe mais daemon non joignable rapidement - etape ignoree"
  fi
else
  warn "Docker non installe - etape ignoree"
fi
echo ""

# ============================================================
# 2. CACHES OUTILS
# ============================================================
echo "── 2. Nettoyage des caches outils ──"

if command_exists npm; then
  NPM_DIR="$HOME/.npm"
  NPM_SIZE="$(dir_size_mb "$NPM_DIR")"
  if (( NPM_SIZE > 50 )); then
    info "Nettoyage cache npm (${NPM_SIZE} Mo)..."
    npm cache clean --force >/dev/null 2>&1 || true
    log "Cache npm nettoye"
  else
    log "Cache npm faible ou absent"
  fi
else
  warn "npm non installe"
fi

if command_exists pip3; then
  PIP_CACHE_DIR="$(pip3 cache dir 2>/dev/null || echo "")"
  if [ -n "$PIP_CACHE_DIR" ] && [ -d "$PIP_CACHE_DIR" ]; then
    PIP_SIZE="$(dir_size_mb "$PIP_CACHE_DIR")"
    if (( PIP_SIZE > 10 )); then
      info "Nettoyage cache pip (${PIP_SIZE} Mo)..."
      pip3 cache purge >/dev/null 2>&1 || true
      log "Cache pip nettoye"
    else
      log "Cache pip faible"
    fi
  else
    log "Aucun cache pip detecte"
  fi
else
  warn "pip3 non installe"
fi

if command_exists yarn; then
  YARN_CACHE_DIR="$(yarn cache dir 2>/dev/null || echo "")"
  if [ -n "$YARN_CACHE_DIR" ] && [ -d "$YARN_CACHE_DIR" ]; then
    YARN_SIZE="$(dir_size_mb "$YARN_CACHE_DIR")"
    if (( YARN_SIZE > 50 )); then
      info "Nettoyage cache yarn (${YARN_SIZE} Mo)..."
      yarn cache clean >/dev/null 2>&1 || true
      log "Cache yarn nettoye"
    else
      log "Cache yarn faible"
    fi
  else
    log "Aucun cache yarn detecte"
  fi
else
  warn "yarn non installe"
fi

if [ "$OS" = "Darwin" ] && command_exists brew; then
  info "Nettoyage Homebrew..."
  brew cleanup -s >/dev/null 2>&1 || true
  brew autoremove >/dev/null 2>&1 || true
  BREW_CACHE="$(brew --cache 2>/dev/null || echo "")"
  if [ -n "$BREW_CACHE" ] && [ -d "$BREW_CACHE" ]; then
    rm -rf "$BREW_CACHE"/* >/dev/null 2>&1 || true
  fi
  log "Homebrew nettoye"
fi
echo ""

# ============================================================
# 3. LOGS ET TEMPORAIRES
# ============================================================
echo "── 3. Logs et fichiers temporaires ──"

if [ "$OS" = "Darwin" ]; then
  if sudo_ready; then
    LOG_SIZE="$(du -sm /private/var/log 2>/dev/null | awk '{print $1+0}')"
    if (( LOG_SIZE > 500 )); then
      info "Logs systeme volumineux (${LOG_SIZE} Mo)"
      sudo rm -rf /private/var/log/asl/*.asl >/dev/null 2>&1 || true
      log "Logs ASL nettoyes"
    else
      log "Logs systeme raisonnables"
    fi
  else
    warn "sudo requis pour nettoyer certains logs macOS - etape ignoree"
  fi

  info "Nettoyage caches macOS/Xcode..."
  rm -rf "$HOME/Library/Caches/com.apple.dt.Xcode" >/dev/null 2>&1 || true
  rm -rf "$HOME/Library/Developer/Xcode/DerivedData" >/dev/null 2>&1 || true
  rm -rf "$HOME/Library/Developer/Xcode/Archives" >/dev/null 2>&1 || true

  DISKIMAGE_GLOBS=(/private/var/folders/*/*/com.apple.DiskImages*)
  if (( ${#DISKIMAGE_GLOBS[@]} > 0 )); then
    rm -rf "${DISKIMAGE_GLOBS[@]}" >/dev/null 2>&1 || true
  fi

  log "Caches macOS/Xcode nettoyes"
elif [ "$OS" = "Linux" ]; then
  if command_exists journalctl; then
    info "Reduction des logs systemd a 7 jours..."
    sudo journalctl --vacuum-time=7d >/dev/null 2>&1 || true
    log "Logs journalctl nettoyes"
  fi
fi

info "Nettoyage des fichiers temporaires..."
find /tmp -type f -mtime +7 -delete 2>/dev/null || true
find /var/tmp -type f -mtime +7 -delete 2>/dev/null || true
log "Fichiers temporaires nettoyes"

if [ "$OS" = "Darwin" ]; then
  TRASH_SIZE="$(dir_size_mb "$HOME/.Trash")"
  if (( TRASH_SIZE > 100 )); then
    warn "Corbeille detectee (${TRASH_SIZE} Mo)"
    warn "Pour vider: rm -rf ~/.Trash/*"
  else
    log "Corbeille faible ou vide"
  fi
fi
echo ""

# ============================================================
# 4. NETTOYAGE PROJET
# ============================================================
echo "── 4. Nettoyage du projet ──"

PYCACHE_COUNT="$(find "$PROJECT_DIR" \
  -path "$PROJECT_DIR/.git" -prune -o \
  -path "$PROJECT_DIR/venv" -prune -o \
  -path "$PROJECT_DIR/.venv" -prune -o \
  -path "$PROJECT_DIR/node_modules" -prune -o \
  -path "$PROJECT_DIR/dashboard/node_modules" -prune -o \
  -type d -name "__pycache__" -print 2>/dev/null | wc -l | tr -d ' ')"

if (( PYCACHE_COUNT > 0 )); then
  info "Suppression de $PYCACHE_COUNT dossier(s) __pycache__..."
  find "$PROJECT_DIR" \
    -path "$PROJECT_DIR/.git" -prune -o \
    -path "$PROJECT_DIR/venv" -prune -o \
    -path "$PROJECT_DIR/.venv" -prune -o \
    -path "$PROJECT_DIR/node_modules" -prune -o \
    -path "$PROJECT_DIR/dashboard/node_modules" -prune -o \
    -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  log "__pycache__ nettoyes"
else
  log "Aucun __pycache__ detecte"
fi

PYC_COUNT="$(find "$PROJECT_DIR" \
  -path "$PROJECT_DIR/.git" -prune -o \
  -path "$PROJECT_DIR/venv" -prune -o \
  -path "$PROJECT_DIR/.venv" -prune -o \
  -path "$PROJECT_DIR/node_modules" -prune -o \
  -path "$PROJECT_DIR/dashboard/node_modules" -prune -o \
  -type f -name "*.pyc" -print 2>/dev/null | wc -l | tr -d ' ')"

if (( PYC_COUNT > 0 )); then
  info "Suppression de $PYC_COUNT fichier(s) .pyc..."
  find "$PROJECT_DIR" \
    -path "$PROJECT_DIR/.git" -prune -o \
    -path "$PROJECT_DIR/venv" -prune -o \
    -path "$PROJECT_DIR/.venv" -prune -o \
    -path "$PROJECT_DIR/node_modules" -prune -o \
    -path "$PROJECT_DIR/dashboard/node_modules" -prune -o \
    -type f -name "*.pyc" -delete 2>/dev/null || true
  log ".pyc supprimes"
else
  log "Aucun .pyc detecte"
fi

if [ -d "$PROJECT_DIR/dashboard/node_modules/.cache" ]; then
  NODE_CACHE_SIZE="$(dir_size_mb "$PROJECT_DIR/dashboard/node_modules/.cache")"
  if (( NODE_CACHE_SIZE > 50 )); then
    info "Nettoyage cache node_modules (${NODE_CACHE_SIZE} Mo)..."
    rm -rf "$PROJECT_DIR/dashboard/node_modules/.cache" >/dev/null 2>&1 || true
    log "Cache node_modules nettoye"
  else
    log "Cache node_modules faible"
  fi
fi

if [ -d "$PROJECT_DIR/dashboard/.next" ]; then
  NEXT_SIZE="$(dir_size_mb "$PROJECT_DIR/dashboard/.next")"
  if (( NEXT_SIZE > 100 )); then
    info "Nettoyage cache .next (${NEXT_SIZE} Mo)..."
    rm -rf "$PROJECT_DIR/dashboard/.next" >/dev/null 2>&1 || true
    log "Cache .next nettoye"
  else
    log "Cache .next faible"
  fi
fi

if [ -f "$HOME/java_error_in_phpstorm.hprof" ]; then
  HPROF_SIZE="$(du -sm "$HOME/java_error_in_phpstorm.hprof" 2>/dev/null | awk '{print $1+0}')"
  info "Dump PhpStorm detecte (${HPROF_SIZE} Mo)"
  warn "Suppression manuelle possible : rm -f ~/java_error_in_phpstorm.hprof"
fi
echo ""

# ============================================================
# 5. RAPPORT FINAL
# ============================================================
echo "── 5. Rapport final ──"
echo ""

AFTER_AVAIL="$(get_avail_kb)"
if (( BEFORE_AVAIL > 0 && AFTER_AVAIL > 0 )); then
  FREED_KB=$(( AFTER_AVAIL - BEFORE_AVAIL ))
  if (( FREED_KB > 0 )); then
    log "Espace total libere: $(bytes_to_human $(( FREED_KB * 1024 )))"
  else
    warn "Aucun gain mesurable immediat"
  fi
fi

info "Espace disque apres nettoyage:"
df -h / 2>/dev/null | tail -1
echo ""

if docker_ready; then
  info "Etat Docker apres nettoyage:"
  docker system df 2>/dev/null || true
else
  warn "Etat Docker non affiche car le daemon ne repond pas rapidement"
fi

echo ""
echo "=========================================="
echo "  Nettoyage termine !"
echo "=========================================="
echo ""