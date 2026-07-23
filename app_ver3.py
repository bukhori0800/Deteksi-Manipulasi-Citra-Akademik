import streamlit as st
import numpy as np
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
from skimage.metrics import mean_squared_error, peak_signal_noise_ratio
import base64
import io

st.set_page_config(page_title="Secure e-Document", page_icon="🛡️", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── ROOT PALETTE — PUTIH & GOLD ──────────────────────────
   Background utama   #ffffff (putih)
   Surface (input bg) #faf7f0 (putih gading lembut)
   Card bg             #ffffff (putih, dibatasi border gold)
   Border              #e8d9b5 (gold pucat)
   Gold accent (utama) #b8902f (gold gelap, kontras cukup di atas putih)
   Gold light (hover)  #d4af37
   Teal accent         #2a8a9c (tetap dipakai sbg aksen sekunder)
   Text primary        #1f2937 (charcoal, BUKAN putih lagi)
   Text muted          #6b7280 (abu medium, masih kebaca di atas putih)
   Navy (dipakai utk teks pada elemen gold) #0d1b2a
──────────────────────────────────────────────────────── */

:root {
    --bg:        #ffffff;
    --surface:   #faf7f0;
    --card:      #ffffff;
    --border:    #e8d9b5;
    --gold:      #b8902f;
    --gold-lt:   #d4af37;
    --teal:      #2a8a9c;
    --teal-dim:  #1f6f80;
    --text:      #1f2937;
    --muted:     #6b7280;
    --ok:        #15803d;
    --ok-bg:     #f0fdf4;
    --err:       #b91c1c;
    --err-bg:    #fef2f2;
    --warn:      #b45309;
    --warn-bg:   #fffbeb;
    --navy:      #0d1b2a;
}

/* ── GLOBAL ──────────────────────────────────────────── */
html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── HEADER ─────────────────────────────────────────── */
.app-header {
    text-align: center;
    padding: 48px 0 28px;
}
.app-header .badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--gold), var(--gold-lt));
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding: 5px 18px;
    border-radius: 100px;
    margin-bottom: 18px;
}
.app-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 48px;
    font-weight: 400;
    color: var(--text);
    margin: 0 0 10px;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.app-header h1 span {
    color: var(--gold);
}
.app-header p {
    color: var(--muted);
    font-size: 15px;
    font-weight: 300;
    margin: 0;
    letter-spacing: 0.3px;
}

/* ── DIVIDER ─────────────────────────────────────────── */
.gold-rule {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold) 40%, var(--gold-lt) 60%, transparent);
    border: none;
    margin: 0 0 36px;
    opacity: 0.7;
}

/* ── TABS ────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 14px;
    padding: 6px;
    border: 1px solid var(--border);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: var(--muted);
    font-weight: 500;
    font-size: 14px;
    letter-spacing: 0.3px;
    padding: 10px 28px;
    background: transparent;
    transition: all 0.25s;
}
.stTabs [data-baseweb="tab"] p {
    color: var(--muted);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-lt) 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}
.stTabs [aria-selected="true"] p {
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"]    { display: none; }

/* ── CARD ────────────────────────────────────────────── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 12px 26px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(184,144,47,0.08);
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--gold), var(--teal));
    border-radius: 18px 18px 0 0;
}
.card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: var(--gold);
    letter-spacing: 0.2px;
    text-align: center;
}

/* teks bebas di dalam card (info panel "Cara Kerja") pakai var(--text)/(--muted), bukan abu gelap hardcoded */
.card-body {
    color: var(--muted);
    font-size: 16px;
    line-height: 1.8;
}

/* ── FILE UPLOADER ───────────────────────────────────── */
div[data-testid="stFileUploader"] > div {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: var(--gold) !important;
}
div[data-testid="stFileUploader"] label {
    color: var(--muted) !important;
    font-size: 13px !important;
}
div[data-testid="stFileUploader"] section {
    background: var(--surface) !important;
}
div[data-testid="stFileUploaderDropzoneInstructions"] span,
div[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: var(--muted) !important;
}

/* ── TEXT INPUTS ─────────────────────────────────────── */
.stTextInput label, .stTextArea label {
    color: var(--muted) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

div[data-testid="textInputRootElement"] {
    padding: 0;
    border: 0;
    border-radius: 14px !important;
}

.stTextInput svg {
    color: var(--muted) !important;
}
.stTextInput svg:hover {
    color: var(--gold) !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    background: transparent !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(184,144,47,0.15) !important;
}
input::placeholder, textarea::placeholder {
    color: #b3a98c !important;
}

/* ── BUTTON ──────────────────────────────────────────── */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-lt) 100%);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.5px;
    border: none;
    padding: 10px 16px;
    transition: all 0.25s;
    box-shadow: 0 4px 20px rgba(184,144,47,0.25);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(184,144,47,0.40);
    color: #ffffff;
}
.stButton > button:active {
    transform: translateY(0);
}
.stButton > button p {
    color: #ffffff !important;
}

/* ── METRIC ──────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
}
div[data-testid="stMetric"] label[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-family: 'DM Serif Display', serif;
    font-size: 24px !important;
}

div[data-testid="stCaptionContainer"] > p {
    color: var(--muted) !important;
    font-size: 15px !important;
}

/* ── CODE BLOCK ──────────────────────────────────────── */
.stCode, pre {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--teal-dim) !important;
    font-size: 13px !important;
}
.stCode code {
    color: var(--teal-dim) !important;
}

/* ── STATUS BOXES ────────────────────────────────────── */
.status-box {
    border-radius: 14px;
    padding: 18px 22px;
    font-weight: 600;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    letter-spacing: 0.2px;
}
.status-ok { background: var(--ok-bg); border: 1px solid rgba(21,128,61,0.25); color: var(--ok); }
.status-err { background: var(--err-bg); border: 1px solid rgba(185,28,28,0.25); color: var(--err); }
.status-warn { background: var(--warn-bg); border: 1px solid rgba(180,83,9,0.25); color: var(--warn); }

/* ── SPINNER ─────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── CAPTION ─────────────────────────────────────────── */
.stCaption { color: var(--muted) !important; font-size: 12px !important; }

/* ── IMAGE ───────────────────────────────────────────── */
.stImage img {
    border-radius: 14px;
    border: 1px solid var(--border);
}

div[data-testid="stImageCaption"] {
    color: var(--gold) !important;
}

/* ── DOWNLOAD BUTTON ───────────────────────────────────── */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, var(--gold), var(--gold-lt)) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    border: none !important;
    transition: all 0.2s !important;
}
div[data-testid="stDownloadButton"] > button p {
    color: #ffffff !important;
}

/* ── PLACEHOLDER STATE (empty card) ───────────────────── */
.empty-state {
    color: #c9bfa3;
}

/* ── SCROLLBAR ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="app-header">
    <div class="badge" style="font-size: 16px;">🛡️ Academic Document Security</div>
    <h1 style="font-size: 60px;">Secure <span>e-Document</span> System</h1>
    <p>Steganografi LSB &amp; Enkripsi AES-256 untuk Validasi Dokumen Akademik</p>
</div>
<hr class="gold-rule">
""", unsafe_allow_html=True)

# ================= HELPER =================
def get_aes_key(password):
    return hashlib.sha256(password.encode()).digest()

def get_seed(password):
    hash_bytes = hashlib.sha256(password.encode()).digest()
    return int.from_bytes(hash_bytes[:4], 'big')

def encrypt_data(plaintext, password):
    key = get_aes_key(password)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return cipher.iv + ct_bytes

def decrypt_data(ciphertext, password):
    try:
        key = get_aes_key(password)
        iv = ciphertext[:16]
        ct = ciphertext[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except:
        return None

def encode_lsb(image, secret_bytes, password):
    img_arr = np.array(image)
    flat_img = img_arr.flatten()

    # convert secret ke binary
    secret_bin = ''.join([format(b, '08b') for b in secret_bytes])
    delimiter = '1111111111111110'
    secret_bin += delimiter

    if len(secret_bin) > len(flat_img):
        raise ValueError("Kapasitas gambar terlalu kecil.")

    #  SEED dari password (biar konsisten & random)
    seed = int(hashlib.sha256(password.encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)

    #  ambil index random sebanyak panjang data
    indices = np.random.choice(len(flat_img), size=len(secret_bin), replace=False)

    # sisipkan ke posisi acak
    for i, bit in enumerate(secret_bin):
        idx = indices[i]
        flat_img[idx] = (flat_img[idx] & 254) | int(bit)

    return flat_img.reshape(img_arr.shape)

def decode_lsb(image, password):
    img_arr = np.array(image)
    flat_img = img_arr.flatten()

    # 🔥 seed HARUS sama
    seed = int(hashlib.sha256(password.encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)

    # ambil semua index dalam urutan yang sama
    indices = np.random.choice(len(flat_img), size=len(flat_img), replace=False)

    extracted_bits = []

    for idx in indices:
        extracted_bits.append(str(flat_img[idx] & 1))

    extracted_bin = ''.join(extracted_bits)

    delimiter = '1111111111111110'
    end_index = extracted_bin.find(delimiter)

    if end_index == -1:
        return None

    valid_bin = extracted_bin[:end_index]

    secret_bytes = bytearray()
    for i in range(0, len(valid_bin), 8):
        byte = valid_bin[i:i+8]
        if len(byte) == 8:
            secret_bytes.append(int(byte, 2))

    return bytes(secret_bytes)

def password_strength(pw):
    score = 0
    if len(pw) > 8: score += 1
    if any(c.isdigit() for c in pw): score += 1
    if any(c.isupper() for c in pw): score += 1
    if any(c in "!@#$%^&*" for c in pw): score += 1
    return score

STRENGTH_LABELS = ["", "Lemah", "Sedang", "Kuat", "Sangat Kuat"]
STRENGTH_COLORS = ["", "#b91c1c", "#b45309", "#15803d", "#15803d"]

# ================= TABS =================
tab1, tab2 = st.tabs(["🔒  Encoding & Enkripsi", "🔓  Verifikasi Dokumen"])

# ================= TAB 1: ENCODING =================
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="card"><div class="card-title">Upload & Konfigurasi</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Pilih Gambar Cover (PNG)", type=["png"])

        text = st.text_area("Data Kredensial", placeholder="Contoh:\nNama: Budi Santoso\nNIM: 12345678\nIPK: 3.85\nStatus: Lulus", height=200)
        password = st.text_input("Password Enkripsi AES", type="password", placeholder="Masukkan password yang kuat…")

        if password:
            strength = password_strength(password)
            st.progress(strength / 4)
            label = STRENGTH_LABELS[strength] if strength > 0 else ""
            color = STRENGTH_COLORS[strength] if strength > 0 else ""
            st.markdown(f'<span style="font-size:12px;font-weight:600;color:{color}">{label}</span>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("🔐 Enkripsi & Sisipkan Data", key="btn_encode")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if uploaded and text and password and run:
            with st.spinner("Sedang memproses…"):
                img = Image.open(uploaded).convert('RGB')
                enc = encrypt_data(text, password)

                try:
                    stego_arr = encode_lsb(img, enc, password)
                    stego_img = Image.fromarray(stego_arr.astype('uint8'))

                    st.markdown('<div class="card"><div class="card-title">Perbandingan Visual</div>', unsafe_allow_html=True)

                    img_col1, img_col2 = st.columns(2)
                    with img_col1:
                        try:
                            st.image(img, caption="Original Image (Asli)", use_container_width=True)
                        except TypeError:
                            st.image(img, caption="Original Image (Asli)", use_column_width=True)

                    with img_col2:
                        try:
                            st.image(stego_img, caption="Stego Image (Tersisip)", use_container_width=True)
                        except TypeError:
                                st.image(stego_img, caption="Stego Image (Tersisip)", use_column_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # Download
                    buf = io.BytesIO()
                    stego_img.save(buf, format="PNG")
                    st.download_button(
                        "⬇️  Download Stego Image",
                        data=buf.getvalue(),
                        file_name="stego_document.png",
                        mime="image/png"
                    )

                    # Metrics Calculation
                    mse = mean_squared_error(np.array(img), stego_arr)
                    psnr = peak_signal_noise_ratio(np.array(img), stego_arr, data_range=255)

                    total_pixels = img.width * img.height * 3
                    used_pixels = len(enc) * 8 + 16
                    capacity_used = (used_pixels / total_pixels) * 100

                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("PSNR (dB)", f"{psnr:.2f}")
                        st.progress(min(psnr / 50, 1.0))
                        st.caption("Semakin tinggi = semakin baik")
                    with c2:
                        st.metric("MSE", f"{mse:.4f}")
                        st.progress(min(mse / 10, 1.0))
                        st.caption("Semakin rendah = semakin baik")
                    with c3:
                        st.metric("Kapasitas", f"{capacity_used:.3f}%")
                        st.progress(min(capacity_used / 100, 1.0))
                        st.caption("Ruang piksel terpakai")

                except ValueError as e:
                    st.markdown(f'<div class="status-box status-err">❌ GAGAL — {e}</div>', unsafe_allow_html=True)

        elif not (uploaded and text and password) and run:
            st.markdown('<div class="status-box status-warn">⚠️  Lengkapi semua field sebelum memproses.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="display:flex;align-items:center;justify-content:center;min-height:260px;">'
                        '<div style="text-align:center;" class="empty-state">'
                        '<div style="font-size:48px;margin-bottom:12px;">🖼️</div>'
                        '<div style="font-size:14px;font-weight:500;color:var(--muted);">Hasil stego image akan tampil di sini</div>'
                        '</div></div>', unsafe_allow_html=True)

# ================= TAB 2: VERIFICATION =================
with tab2:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="card"><div class="card-title">Upload & Verifikasi</div>', unsafe_allow_html=True)
        uploaded_v = st.file_uploader("Upload Stego Image (PNG)", type=["png"], key="v_upload")
        password_v = st.text_input("Password Dekripsi", type="password", placeholder="Masukkan password yang sama saat enkripsi…", key="v_pass")
        st.markdown("<br>", unsafe_allow_html=True)
        run_v = st.button("🔍  Verifikasi Keaslian Dokumen", key="btn_verify")
        st.markdown('</div>', unsafe_allow_html=True)

        # Info panel
        st.markdown("""
        <div class="card" style="margin-top:0">
            <div class="card-title">Cara Kerja</div>
            <div class="card-body">
                <b style="color:var(--gold)">1. LSB Extraction</b><br>
                Bit terendah setiap pixel dibaca untuk merekonstruksi byte tersembunyi.<br><br>
                <b style="color:var(--teal)">2. AES-256 Decryption</b><br>
                Data didekrip menggunakan password Anda. Jika password salah atau gambar dimanipulasi, proses gagal.<br><br>
                <b style="color:var(--ok)">3. Validasi</b><br>
                Kredensial yang berhasil didekripsi membuktikan keaslian dokumen.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if uploaded_v and password_v and run_v:
            with st.spinner("Mengekstrak dan mendekripsi…"):
                img_v = Image.open(uploaded_v).convert('RGB')
                data = decode_lsb(img_v, password_v)

            if data:
                dec = decrypt_data(data, password_v)
                if dec:
                    st.markdown('<div class="status-box status-ok">✅  DOKUMEN VALID — Data berhasil diverifikasi</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card"><div class="card-title">Isi Kredensial Tersembunyi</div>', unsafe_allow_html=True)
                    st.text_area("Data Terdekripsi:", value=dec, height=200, disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        st.image(img_v, caption="Stego image yang diverifikasi", use_container_width=True)
                    except TypeError:
                        st.image(img_v, caption="Stego image yang diverifikasi", use_column_width=True)
                else:
                    st.markdown('<div class="status-box status-err">❌  GAGAL — Password salah atau dokumen telah dimanipulasi</div>', unsafe_allow_html=True)
                    st.markdown("""
                    <div class="card">
                        <div class="card-body">
                            Kemungkinan penyebab:<br>
                            &nbsp;• Password tidak sesuai dengan yang digunakan saat enkripsi<br>
                            &nbsp;• File gambar telah dikompresi, di-crop, atau dimodifikasi<br>
                            &nbsp;• Gambar dikonversi ke format lain (JPG/WEBP) yang merusak LSB
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-box status-warn">⚠️  Tidak ditemukan data tersembunyi dalam gambar ini</div>', unsafe_allow_html=True)

        elif not (uploaded_v and password_v) and run_v:
            st.markdown('<div class="status-box status-warn">⚠️  Upload gambar dan masukkan password terlebih dahulu.</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="display:flex;align-items:center;justify-content:center;min-height:320px;">
                <div style="text-align:center;" class="empty-state">
                    <div style="font-size:52px;margin-bottom:14px;">🔍</div>
                    <div style="font-size:14px;font-weight:500;margin-bottom:6px;color:var(--muted);">Siap memverifikasi</div>
                    <div style="font-size:12px;color:var(--muted);">Upload stego image dan masukkan password</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
