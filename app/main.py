from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from pathlib import Path
from .models import UserCreate, UserOut, PlaylistCreate, PlaylistUpdate, PlaylistOut 
from .repositories import (
    create_user,
    get_user,
    create_playlist,
    get_playlist,
    list_playlists_visible_to,
    update_playlist,
    delete_playlist,
)

# -----------------------------------------------------------------------------
# FastAPI app setup
# -----------------------------------------------------------------------------
app = FastAPI(title="Music Playlist Manager", version="0.1.0")

# Create static file directory to add HTML GUI
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

def current_user_id(x_user_id: Optional[str]) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id

# -----------------------------------------------------------------------------
# System / health
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    """
    Health check
    """
    return {"status": "ok"}

# -----------------------------------------------------------------------------
# Users
# -----------------------------------------------------------------------------
@app.post("/users", response_model=UserOut)
def create_user_api(payload: UserCreate):
    """
    Create user document
    """
    return create_user(payload)

@app.get("/users/{user_id}", response_model=UserOut)
def get_user_api(user_id: str):
    """
    Fetch user by their ID
    """
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

# -----------------------------------------------------------------------------
# Playlists
# -----------------------------------------------------------------------------

@app.post("/playlists", response_model=PlaylistOut)
def create_playlist_api(payload: PlaylistCreate, x_user_id: Optional[str] = Header(default=None)):
    """
    Create a new playlist for the user
    """
    uid = current_user_id(x_user_id)
    return create_playlist(uid, payload)

@app.get("/playlists/{playlist_id}", response_model=PlaylistOut)
def get_playlist_api(playlist_id: str, x_user_id: Optional[str] = Header(default=None)):
    """
    Fetch a playlist by the ID
    """
    uid = current_user_id(x_user_id)
    p = get_playlist(playlist_id)
    if not p:
        raise HTTPException(404, "Not found")
    if (uid != p.owner_id) and (uid not in p.collaborator_ids) and (not p.is_public):
        raise HTTPException(403, "Not allowed")
    return p

@app.get("/playlists", response_model=List[PlaylistOut])
def list_playlists_api(x_user_id: Optional[str] = Header(default=None)):
    """
    Lists playlist that the user has
    """
    uid = current_user_id(x_user_id)
    return list_playlists_visible_to(uid)

@app.patch("/playlists/{playlist_id}", response_model=PlaylistOut)
def update_playlist_api(playlist_id: str, payload: PlaylistUpdate, x_user_id: Optional[str] = Header(default=None)):
    uid = current_user_id(x_user_id)
    try:
        updated = update_playlist(playlist_id, uid, payload)
    except PermissionError:
        raise HTTPException(403, "Not allowed")
    if not updated:
        raise HTTPException(404, "Not found")
    return updated

@app.delete("/playlists/{playlist_id}")
def delete_playlist_api(playlist_id: str, x_user_id: Optional[str] = Header(default=None)):
    uid = current_user_id(x_user_id)
    try:
        ok = delete_playlist(playlist_id, uid)
    except PermissionError:
        raise HTTPException(403, "Not allowed")
    if not ok:
        raise HTTPException(404, "Not found")
    return {"deleted": True}
