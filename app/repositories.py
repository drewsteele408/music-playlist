from typing import List, Optional 
from datetime import datetime, timezone
from .db import get_db
from .models import (
    PlaylistCreate, 
    PlaylistUpdate, 
    PlaylistOut, 
    Track, 
    UserCreate, 
    UserOut
)

# --------------------------------
# Return current datetime 
# --------------------------------

def _current_utc_time():
    return datetime.now(timezone.utc)

# --------------------------------
# User repository functions
# --------------------------------

def create_user(user_data: UserCreate) -> UserOut:
    """
    Create a new user in Firestone database
    """
    firestone_client = get_db
    user_document = firestone_client.collection("users").document(user_data.user_id)

    user_document.set({
        "display_name": user_data.display_name, 

    })

    return UserOut(user_id=user_data.user_id, display_name=user_data.display_name)

def get_user(user_id: str) -> Optional[UserOut]:
    """
    Retrieve a single user from the firestore database by ID
    """

    firestore_client = get_db()
    user_snapshot = firestore_client.collection("users").document(user_id).get()

    if not user_snapshot.exists:
        return None
    
    user_data = user_snapshot.to_dict()
    return UserOut(
        user_id=user_id, 
        display_name=user_data.get("display_name", "")
    )

# --------------------------------
# Playlist repository functions
# --------------------------------

def create_playlist(owner_id: str, playlist_data: PlaylistCreate) -> PlaylistOut:
    """
    Create a new playlist in Firestore database
    """
    firestore_client = get_db()
    playlist_document = firestore_client.collection("playlists").document()
    timestamp_now = _current_utc_time()

    playlist_record = {
        "owner_id": owner_id,
        "name": playlist_data.name, 
        "description": playlist_data.description,
        "is_public": playlist_data.is_public,
        "collaborator_ids": playlist_data.collaborator_ids,
        "tracks": [track.model_dump() for track in playlist_data.tracks],
        "created_at": timestamp_now,
        "updated_at": timestamp_now,
    }

    playlist_document.set(playlist_record)

    return PlaylistOut(id=playlist_document.id, **playlist_record)

def get_playlist(playlist_id: str) -> Optional[PlaylistOut]:
    """
    Retrieve a single playlist document from Firestore.
    """
    firestore_client = get_db()
    playlist_snapshot = firestore_client.collection("playlists").document(playlist_id).get()

    if not playlist_snapshot.exists:
        return None

    playlist_data = playlist_snapshot.to_dict()

    return PlaylistOut(
        id=playlist_id,
        owner_id=playlist_data["owner_id"],
        name=playlist_data["name"],
        description=playlist_data.get("description"),
        is_public=playlist_data.get("is_public", False),
        collaborator_ids=playlist_data.get("collaborator_ids", []),
        tracks=[Track(**track) for track in playlist_data.get("tracks", [])],
        created_at=playlist_data.get("created_at"),
        updated_at=playlist_data.get("updated_at"),
    )


def list_playlists_visible_to(user_id: str) -> List[PlaylistOut]:
    """
    Return a list of playlists that the given user can view.
    """
    firestore_client = get_db()
    playlist_collection = firestore_client.collection("playlists")

    # Query playlists by visibility type
    owned_playlists = playlist_collection.where("owner_id", "==", user_id).stream()
    collaborative_playlists = playlist_collection.where("collaborator_ids", "array_contains", user_id).stream()
    public_playlists = playlist_collection.where("is_public", "==", True).stream()

    collected_playlists: List[PlaylistOut] = []
    seen_playlist_ids = set()

    # Combine results, avoiding duplicates
    for playlist_group in (owned_playlists, collaborative_playlists, public_playlists):
        for playlist_snapshot in playlist_group:
            if not playlist_snapshot.exists:
                continue
            if playlist_snapshot.id in seen_playlist_ids:
                continue

            seen_playlist_ids.add(playlist_snapshot.id)
            playlist_data = playlist_snapshot.to_dict()

            collected_playlists.append(
                PlaylistOut(
                    id=playlist_snapshot.id,
                    owner_id=playlist_data["owner_id"],
                    name=playlist_data["name"],
                    description=playlist_data.get("description"),
                    is_public=playlist_data.get("is_public", False),
                    collaborator_ids=playlist_data.get("collaborator_ids", []),
                    tracks=[Track(**track) for track in playlist_data.get("tracks", [])],
                    created_at=playlist_data.get("created_at"),
                    updated_at=playlist_data.get("updated_at"),
                )
            )

    return collected_playlists


def update_playlist(playlist_id: str, user_id: str, updated_data: PlaylistUpdate) -> Optional[PlaylistOut]:
    """
    Update fields in an existing playlist if the user has permission.
    """
    firestore_client = get_db()
    playlist_document = firestore_client.collection("playlists").document(playlist_id)
    playlist_snapshot = playlist_document.get()

    if not playlist_snapshot.exists:
        return None

    playlist_data = playlist_snapshot.to_dict()

    # Permission: must be owner or collaborator
    if user_id != playlist_data["owner_id"] and user_id not in playlist_data.get("collaborator_ids", []):
        raise PermissionError("User is not allowed to modify this playlist.")

    update_fields = {}
    for field_name in ["name", "description", "is_public", "tracks", "collaborator_ids"]:
        new_value = getattr(updated_data, field_name)
        if new_value is not None:
            update_fields[field_name] = [track.dict() for track in new_value] if field_name == "tracks" else new_value

    if update_fields:
        update_fields["updated_at"] = _current_utc_time()
        playlist_document.update(update_fields)

    return get_playlist(playlist_id)


def delete_playlist(playlist_id: str, user_id: str) -> bool:
    """
    Delete a playlist from Firestore if the user is the owner.
    """
    firestore_client = get_db()
    playlist_document = firestore_client.collection("playlists").document(playlist_id)
    playlist_snapshot = playlist_document.get()

    if not playlist_snapshot.exists:
        return False

    playlist_data = playlist_snapshot.to_dict()

    if user_id != playlist_data["owner_id"]:
        raise PermissionError("Only the playlist owner can delete it.")

    playlist_document.delete()
    return True