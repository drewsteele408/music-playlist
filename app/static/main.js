const state = { tracks: [] };

// Call the FastAPI endpoints
const api = (path, opts = {}) => {
  const uid = document.getElementById("uid").value.trim();
  const headers = {
    "X-User-Id": uid,
    "Content-Type": "application/json",
    ...(opts.headers || {}),
  };
  return fetch(path, { ...opts, headers });
};


// Render the list of tracks in the tracks array 
function renderTracks() {
  const tbody = document.querySelector("#tracksTable tbody");
  tbody.innerHTML = "";
  // Loop over each track and create a row for it
  state.tracks.forEach((t, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${t.title}</td>
            <td>${t.artist}</td>
            <td>${t.duration_sec ?? ""}</td>
            <td>${t.external_url ?? ""}</td>
            <td><button data-i="${i}" class="remove">Remove</button></td>
          `;
    tbody.appendChild(tr);
  });

  // Get the remove buttons to work and remove a track from local list
  tbody.querySelectorAll("button.remove").forEach((btn) => {
    btn.onclick = () => {
      state.tracks.splice(+btn.dataset.i, 1);
      renderTracks();
    };
  });
}


// Called when the "Add Track" button is clicked
document.getElementById("addTrackBtn").onclick = () => {
// Read all input values
  const title = document.getElementById("tTitle").value.trim();
  const artist = document.getElementById("tArtist").value.trim();
  const durationRaw = document.getElementById("tDuration").value.trim();
  const external_url = document.getElementById("tUrl").value.trim();
  if (!title || !artist) return alert("Title and Artist are required");
  const duration_sec = durationRaw ? Number(durationRaw) : undefined;
  if (durationRaw && (isNaN(duration_sec) || duration_sec < 0))
    return alert("Duration must be a non-negative number");
// Add a new track to the array
  state.tracks.push({
    title,
    artist,
    duration_sec,
    external_url: external_url || undefined,
  });

// Clear the form after adding tracks
  document.getElementById("tTitle").value = "";
  document.getElementById("tArtist").value = "";
  document.getElementById("tDuration").value = "";
  document.getElementById("tUrl").value = "";
// Refresh table
  renderTracks();
};

// Used for create playlist button
document.getElementById("createBtn").onclick = async () => {
// Read playlist info
  const name = document.getElementById("plName").value.trim();
  if (!name) return alert("Enter a playlist name");
  const description = document.getElementById("plDesc").value.trim() || null;
  const is_public = document.getElementById("plPublic").checked;

  // Build the playlist object and send to backend
  const body = JSON.stringify({
    name,
    description,
    is_public,
    collaborator_ids: [],
    tracks: state.tracks,
  });

  // Send request to FastAPI enpoint
  const res = await api("/playlists", { method: "POST", body });
  const text = await res.text();
  // Display backend response to the <pre id="out"> area
  document.getElementById("out").textContent = text;
  if (res.ok) {
    state.tracks = [];
    renderTracks();
  }
};

// Load playlist

document.getElementById("loadBtn").onclick = async () => {
  const res = await api("/playlists");
  document.getElementById("out").textContent = await res.text();
};
