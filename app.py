import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# 1. Konfigurasi Halaman Web (Lebar Maksimal agar Nyaman Membaca)
st.set_page_config(page_title="Academic Copilot Pro", page_icon="🎓", layout="wide")

# Muat API Key dari file .env
load_dotenv()

# Konfigurasi koneksi ke Gemini API
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 2. Inisialisasi Memori Struktur Jurnal (Menyimpan Teks Per Bab)
if "riset" not in st.session_state:
    st.session_state.riset = {
        "Topik": "",
        "Bab 1: Pendahuluan": "Belum dibuat. Tentukan topik di sidebar lalu klik Mulai.",
        "Bab 2: Tinjauan Pustaka": "Belum dibuat. Tentukan topik di sidebar lalu klik Mulai.",
        "Bab 3: Metodologi Penelitian": "Belum dibuat. Tentukan topik di sidebar lalu klik Mulai.",
        "Bab 4: Pembahasan & Analisis": "Belum dibuat. Tentukan topik di sidebar lalu klik Mulai.",
        "Bab 5: Kesimpulan & Referensi": "Belum dibuat. Tentukan topik di sidebar lalu klik Mulai."
    }

# 3. Desain Antarmuka Sidebar (Kendali Utama)
with st.sidebar:
    st.header("⚙️ Papan Kendali Proyek")
    topik_input = st.text_input("Fokus Topik / Judul Karya Ilmiah:", placeholder="Masukkan topik riset Anda...")
    
    if st.button("Generate Draf Awal Bersama 🚀", type="primary"):
        if topik_input:
            st.session_state.riset["Topik"] = topik_input
            
            # Sistem prompt ketat untuk memicu penulisan akademis profesional
            base_instruction = (
                "Anda adalah Senior Research Professor. Tulis draf ilmiah yang SANGAT PANJANG, "
                "substantif, formal, penuh dengan terminologi akademik, dan menyertakan sitasi gaya APA yang realistis "
                "(misal: Sukarmo, 2024; Green & Zhang, 2025) berdasarkan basis data jurnal bereputasi. "
                "JANGAN memberikan ringkasan. Berikan analisis mendalam."
            )
            
            # AI menghasilkan draf untuk masing-masing bab secara spesifik agar tidak lelah/terpotong
            for bab in st.session_state.riset.keys():
                if bab == "Topik": continue
                with st.spinner(f"Mengonseptualisasikan {bab}..."):
                    try:
                        response = client.chat.completions.create(
                            model="gemini-2.5-flash",
                            messages=[
                                {"role": "system", "content": base_instruction},
                                {"role": "user", "content": f"Tuliskan secara sangat mendalam, panjang, dan spesifik untuk bagian '{bab}' dari penelitian berjudul: {topik_input}."}
                            ]
                        )
                        st.session_state.riset[bab] = response.choices[0].message.content
                    except Exception as e:
                        st.session_state.riset[bab] = f"Gagal generate: {e}"
            st.rerun()
        else:
            st.sidebar.error("Ketik topik terlebih dahulu!")

# 4. Tampilan Halaman Utama (Sistem Tab)
st.title("🎓 Academic AI Copilot — Workspace Modular")
if st.session_state.riset["Topik"]:
    st.subheader(f"📁 Proyek Aktif: {st.session_state.riset['Topik']}")
else:
    st.info("👋 Selamat datang! Silakan masukkan topik riset Anda di sidebar kiri, lalu klik 'Generate Draf Awal Bersama' untuk memulai kerja cerdas AI.")

# Membuat 5 Tab di Website
tabs = st.tabs(["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

# Mengisi Konten dan Fitur Revisi pada Masing-Masing Tab
for i, bab_name in enumerate(list(st.session_state.riset.keys())[1:]):
    with tabs[i]:
        st.header(bab_name)
        
        # Tampilkan teks bab saat ini
        st.markdown(st.session_state.riset[bab_name])
        
        st.markdown("---")
        # Kolom instruksi revisi KHUSUS untuk bab ini saja
        st.subheader(f"🛠️ Hub dan Perintah Revisi ({bab_name})")
        instruksi_revisi = st.text_area(
            f"Ketik perintah spesifik untuk menyempurnakan {bab_name}:",
            placeholder="Contoh: 'Perpanjang bagian ini 3 paragraf lagi, tambahkan analisis data kuantitatif, dan masukkan 3 sitasi jurnal internasional bereputasi terbaru.'",
            key=f"input_{bab_name}"
        )
        
        if st.button(f"Kembangkan & Revisi {bab_name} 🚀", key=f"btn_{bab_name}"):
            if instruksi_revisi:
                with st.spinner(f"AI sedang merombak dan memperdalam {bab_name} sesuai arahan Anda..."):
                    try:
                        response = client.chat.completions.create(
                            model="gemini-2.5-flash",
                            messages=[
                                {"role": "system", "content": "Anda adalah Profesor Ahli. Tugas Anda adalah merevisi teks karya ilmiah yang diberikan berdasarkan perintah pengguna. Buat teks hasil revisi menjadi SANGAT PANJANG, JAUH LEBIH MENDALAM, menggunakan bahasa akademik tingkat tinggi, serta perbaiki sitasi agar kokoh."},
                                {"role": "user", "content": f"Teks Asli Saat Ini:\n\n{st.session_state.riset[bab_name]}"},
                                {"role": "user", "content": f"Perintah Perubahan/Pengembangan:\n\n{instruksi_revisi}"}
                            ]
                        )
                        # Timpa teks bab lama dengan hasil revisi yang lebih sempurna dan panjang
                        st.session_state.riset[bab_name] = response.choices[0].message.content
                        st.success("Bagian berhasil diperbarui!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal merevisi: {e}")
            else:
                st.warning("Silakan tulis instruksi revisi Anda terlebih dahulu!")