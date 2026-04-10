import os
import tarfile
import h5py
import pandas as pd
import tempfile

TAR_PATH = r"C:\Users\ADMIN\Downloads\millionsongsubset.tar.gz"
OUTPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "local_10k_songs.csv"))


def extract_and_build():
    print("=" * 60)
    print("Rebuilding MSD Pipeline with Full Audio DNA Features")
    print(f"Target: {TAR_PATH}")
    print("=" * 60)

    if not os.path.exists(TAR_PATH):
        print(f"ERROR: Could not locate dataset at {TAR_PATH}")
        return

    records = []

    with tarfile.open(TAR_PATH, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.name.endswith('.h5')]
        print(f"Found {len(members)} song nodes in archive. Extracting audio DNA...")

        tmp_dir = tempfile.mkdtemp()
        tmp_h5_path = os.path.join(tmp_dir, "processing.h5")

        for i, member in enumerate(members):
            if i > 0 and i % 1000 == 0:
                print(f"  -> Processed {i}/{len(members)} tracks...")

            try:
                with tar.extractfile(member) as f_in:
                    with open(tmp_h5_path, "wb") as f_out:
                        f_out.write(f_in.read())

                with h5py.File(tmp_h5_path, 'r') as f:
                    # ── Metadata ──
                    title  = f['metadata']['songs']['title'][0].decode('utf-8', errors='ignore').strip()
                    artist = f['metadata']['songs']['artist_name'][0].decode('utf-8', errors='ignore').strip()
                    terms_array = f['metadata']['artist_terms'][:]
                    terms = " ".join(t.decode('utf-8', errors='ignore') for t in terms_array[:10])

                    # ── Audio Analysis DNA ──
                    tempo       = float(f['analysis']['songs']['tempo'][0])
                    loudness    = float(f['analysis']['songs']['loudness'][0])
                    energy      = float(f['analysis']['songs']['energy'][0])        # 0.0 - 1.0
                    danceability= float(f['analysis']['songs']['danceability'][0])  # 0.0 - 1.0
                    key         = int(f['analysis']['songs']['key'][0])             # 0-11
                    mode        = int(f['analysis']['songs']['mode'][0])            # 0=minor, 1=major
                    duration    = float(f['analysis']['songs']['duration'][0])

                    if not title or not artist:
                        continue

                    records.append({
                        "name"         : title,
                        "artist"       : artist,
                        "vibes"        : terms,
                        "tempo"        : round(tempo, 2),
                        "loudness"     : round(loudness, 2),
                        "energy"       : round(energy, 4),
                        "danceability" : round(danceability, 4),
                        "key"          : key,
                        "mode"         : mode,   # 0=minor, 1=major
                        "duration"     : round(duration, 1)
                    })

            except Exception:
                pass  # Some nodes have corrupt/missing fields; skip silently

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_CSV, index=False)

    print("=" * 60)
    print(f"Done! Extracted audio DNA for {len(records)} tracks.")
    print(f"Saved to: {OUTPUT_CSV}")
    print(f"Columns: {list(df.columns)}")
    print(df[['name', 'artist', 'tempo', 'energy', 'danceability', 'mode']].head(5).to_string())
    print("=" * 60)


if __name__ == "__main__":
    extract_and_build()
