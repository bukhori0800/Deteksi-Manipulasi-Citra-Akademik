import streamlit as st
import numpy as np
from PIL import Image
import hashlib

# ==========================================
# 1. HELPER & CORE FUNCTIONS
# ==========================================

def get_seed(password):
    """Menghasilkan seed integer dari hash SHA-256 password"""
    return int(hashlib.sha256(password.encode()).hexdigest(), 16) % (2**32)

def calculate_sha256(data_bytes):
    """Menghitung nilai SHA-256 dari bytes data"""
    return hashlib.sha256(data_bytes).hexdigest()

def encode_lsb(image, secret_bytes, password):
    img_arr = np.array(image)
    flat_img = img_arr.flatten()

    # Convert secret ke binary + delimiter
    secret_bin = ''.join([format(b, '08b') for b in secret_bytes])
    delimiter = '1111111111111110'  # Pembatas data LSB
    secret_bin += delimiter

    if len(secret_bin) > len(flat_img):
        raise ValueError("Kapasitas gambar terlalu kecil untuk menampung pesan ini.")

    # Generate Seed dari Password
    seed = get_seed(password)
    np.random.seed(seed)

    # PERBAIKAN: Gunakan permutation agar urutan indeks teracak konsisten
    indices = np.random.permutation(len(flat_img))

    # Sisipkan bit pesan pada LSB piksel hasil acakan
    for i, bit in enumerate(secret_bin):
        idx = indices[i]
        flat_img[idx] = (flat_img[idx] & 254) | int(bit)

    return flat_img.reshape(img_arr.shape)


def decode_lsb(image, password):
    img_arr = np.array(image)
    flat_img = img_arr.flatten()

    # Seed HARUS sama persis dengan proses encoding
    seed = get_seed(password)
    np.random.seed(seed)

    # PERBAIKAN: Permutation menjamin urutan acak 100% identik dengan encode
    indices = np.random.permutation(len(flat_img))

    extracted_bits = []
    delimiter = '1111111111111110'

    # Ekstrak bit LSB sesuai urutan acak
    for idx in indices:
        extracted_bits.append(str(flat_img[idx] & 1))
        
        # Optimization: Hentikan ekstraksi jika delimiter ditemukan
        extracted_bin = ''.join(extracted_bits)
        if delimiter in extracted_bin:
            break

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


# ==========================================
# 2. STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Steganografi LSB + SHA-256", layout="wide")

st.title("🔒 Aplikasi Steganografi LSB & Verifikasi SHA-256")
st.write("Sembunyikan pesan rahasia di dalam gambar dan verifikasi integritasnya menggunakan Hash Key.")

tab1, tab2 = st.tabs(["📥 Embed (Sembunyikan Pesan)", "🔍 Extract & Verifikasi"])

# ------------------------------------------
# TAB 1: EMBEDDING
# ------------------------------------------
with tab1:
    st.header("Sembunyikan Pesan ke Dalam Gambar")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_img = st.file_uploader("Upload Gambar Cover (PNG direkomendasikan)", type=["png", "jpg", "jpeg"], key="embed_img")
        secret_text = st.text_area("Masukkan Pesan Rahasia", placeholder="Ketik pesan rahasia di sini...")
        key_password = st.text_input("Masukkan Key / Kunci Akses", type="password", key="embed_key")
        
        btn_embed = st.button("Proses Steganografi", type="primary")

    with col2:
        if btn_embed:
            if not uploaded_img or not secret_text or not key_password:
                st.warning("⚠️ Harap lengkapi semua input (Gambar, Pesan, dan Kunci)!")
            else:
                try:
                    cover_image = Image.open(uploaded_img).convert("RGB")
                    secret_bytes = secret_text.encode('utf-8')

                    # 1. Hitung SHA-256 Asli
                    original_hash = calculate_sha256(secret_bytes)

                    # 2. Lakukan LSB Encoding
                    stego_arr = encode_lsb(cover_image, secret_bytes, key_password)
                    stego_image = Image.fromarray(stego_arr.astype('uint8'))

                    # 3. Simpan Gambar ke Buffer untuk Download
                    import io
                    img_byte_arr = io.BytesIO()
                    stego_image.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()

                    st.success("✅ Pesan berhasil disembunyikan!")
                    st.subheader("Hasil Steganografi:")
                    st.image(stego_image, caption="Gambar Stego (Sudah Terisi Data)", use_column_width=True)

                    st.info(f"**Hash SHA-256 Pesan Asli:**\n`{original_hash}`")
                    st.caption("💡 Simpan nilai Hash SHA-256 di atas untuk dicocokkan pada Tab Verifikasi.")

                    st.download_button(
                        label="💾 Download Gambar Stego (PNG)",
                        data=img_bytes,
                        file_name="stego_image.png",
                        mime="image/png"
                    )

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")

# ------------------------------------------
# TAB 2: EXTRACTION & VERIFICATION
# ------------------------------------------
with tab2:
    st.header("Ekstrak Pesan & Verifikasi Integritas Data")
    
    col1, col2 = st.columns(2)
    with col1:
        stego_upload = st.file_uploader("Upload Gambar Stego", type=["png"], key="extract_img")
        extract_key = st.text_input("Masukkan Kunci Akses (Harus Sama)", type="password", key="extract_key")
        expected_hash = st.text_input("Masukkan Hash SHA-256 Asli (Untuk Verifikasi)", key="extract_hash")
        
        btn_extract = st.button("Ekstrak & Verifikasi", type="primary")

    with col2:
        if btn_extract:
            if not stego_upload or not extract_key:
                st.warning("⚠️ Harap upload Gambar Stego dan isi Kunci Akses!")
            else:
                try:
                    stego_img = Image.open(stego_upload).convert("RGB")
                    
                    # 1. Ekstrak Bytes Rahasia dari LSB
                    extracted_bytes = decode_lsb(stego_img, extract_key)

                    if extracted_bytes is None:
                        st.error("❌ Gagal mengekstrak data! Kemungkinan Kunci Akses salah atau gambar tidak mengandung data.")
                    else:
                        # 2. Dekode Bytes ke Teks
                        try:
                            extracted_text = extracted_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            extracted_text = "[Teks tidak valid / rusak]"

                        # 3. Hitung Hash dari Hasil Ekstraksi
                        current_hash = calculate_sha256(extracted_bytes)

                        st.subheader("📩 Pesan Tersebunyi:")
                        st.code(extracted_text)

                        st.markdown("---")
                        st.subheader("🔍 Hasil Verifikasi Hash SHA-256:")
                        st.write(f"**Hash Data Terekstrak:** `{current_hash}`")

                        # 4. Verifikasi Integritas jika Kunci Hash Asli Dimasukkan
                        if expected_hash:
                            st.write(f"**Hash Ekspektasi (Asli):** `{expected_hash.strip()}`")
                            
                            if current_hash.lower() == expected_hash.strip().lower():
                                st.success("🎉 **VERIFIKASI BERHASIL!** Data Utuh dan tidak mengalami perubahan/kerusakan (Valid).")
                            else:
                                st.error("🚨 **VERIFIKASI GAGAL!** Hash tidak cocok. Data telah dimodifikasi atau Kunci Akses salah.")
                        else:
                            st.info("ℹ️ Masukkan Hash SHA-256 Asli di kolom sebelah kiri untuk melakukan verifikasi integritas otentik.")

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat ekstraksi: {str(e)}")
