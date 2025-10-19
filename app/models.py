from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


# -------------------------------------
# Track model
# -------------------------------------
#Gets metadata for each track that includes things like title, artist, etc. 
class Track(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    duration_sec: Optional[int] = Field(default=None, ge=0)
    external_url: Optional[HttpUrl] = None

# -------------------------------------
# Create Playlist model
# -------------------------------------
# Used to create a new playlist

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    tracks: List[Track] = []
    collaborator_ids: List[str] = []

# -------------------------------------
# Update Playlist model
# -------------------------------------
# Used when you are updating a playlist

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False
    tracks: List[Track] = []
    collaborator_ids: List[str] = []

# -------------------------------------
# Playlist Out model
# -------------------------------------
# This represents a playlist that was returned from the API

class PlaylistOut(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str] = None
    is_public: bool 
    collaborator_ids: List[str]
    tracks: List[Track]
    created_at: datetime
    updated_at: datetime

# -------------------------------------
# Create User model
# -------------------------------------
# Used to create a new user

class UserCreate(BaseModel):
    user_id: str
    display_name: str

# -------------------------------------
# User Out model
# -------------------------------------
# Used to represent a user that was returned from the API

class UserOut(BaseModel):
    user_id: str
    display_name: str

