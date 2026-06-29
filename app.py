import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

st.set_page_config(page_title="Adaptive Academic AI v3", page_icon="🎓", layout="wide")

load_dotenv()

api_key_env = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_env) if api_key_env else None

# Inisialisasi Struktur Memori Aplikasi + Memori Gaya Bahasa Manusia
if "riset" not in st.session_state:
    st.session_state.riset = {
        "Topik": "",
        "Bab 1: Pendahuluan": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 2: Tinjauan Pustaka": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 3: Metodologi Penelitian": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 4: Pembahasan & Analisis": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 5: Kesimpulan & Referensi": "Belum dibuat. Klik tombol di bawah untuk mulai."
    }

if "references_pool" not in st.session_state:
    st.session_state.references_pool = []

# Fitur Kunci: Memori Pembelajaran AI dari Kritik Manusia
if "ai_learning_logs" not in st.session_state:
    st.session_state.ai_learning_logs = []

with st.sidebar:
    st.header("⚙️ Papan Kendali Proyek")
    topik_input = st.text_input("Fokus Topik / Judul Karya Ilmiah:", placeholder="Masukkan topik riset...")
    
    if st.button("Kunci Judul Proyek 🔒", type="primary"):
        if topik_input:
            st.session_state.riset["Topik"] = topik_input
            st.rerun()

    st.write("---")
    st.header("🧠 Buku Catatan Gaya Bahasa (AI Learning)")
    st.write("Tuliskan karakteristik tulisan manusia yang Anda inginkan agar AI terus mengingatnya:")
    gaya_bahasa_user = st.text_area(
        "Panduan Gaya Penulisan:",
        placeholder="Contoh: 'Gunakan kalimat aktif, hindari pengulangan kata kata yang sama, buat narasi mengalir dengan jembatan antar-paragraf yang halus, sertakan istilah lokal Sumbawa Barat secara natural.'"
    )

st.title("🎓 Academic AI Copilot — Self-Learning Workspace")

if st.session_state.riset["Topik"]:
    st.subheader(f"📁 Proyek Aktif: {st.session_state.riset['Topik']}")
else:
    st.info("👋 Silakan kunci judul proyek Anda di sidebar untuk mengaktifkan lembar kerja.")

tabs = st.tabs(["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "📚 Daftar Pustaka", "💾 Ekspor"])

# Menyusun Instruksi yang Menggabungkan Hasil Pembelajaran AI dari Kritik Pengguna
base_instruction = (
    "Anda adalah Senior Research Professor yang menulis dengan gaya humanis, mengalir, mendalam, dan tidak kaku seperti robot. "
    "Hindari pola kalimat template yang membosankan. Tulis secara organik, formal, namun tajam secara analitis."
)

if gaya_bahasa_user:
    base_instruction += f"\n\n[PANDUAN GAYA BAHASA UTAMA DARI USER]: {gaya_bahasa_user}"

if st.session_state.ai_learning_logs:
    base_instruction += f"\n\n[PELAJARAN DARI KOREKSI SEBELUMNYA - JANGAN ULANGI KESALAHAN INI]:\n" + "\n".join(st.session_state.ai_learning_logs)

# Loop Pengerjaan Bab
for i, bab_name in enumerate(list(st.session_state.riset.keys())[1:]):
    with tabs[i]:
        st.header(bab_name)
        st.markdown(st.session_state.riset[bab_name])
        st.markdown("---")
        
        if st.session_state.riset["Topik"] and client:
            if "Belum dibuat" in st.session_state.riset[bab_name]:
                if st.button(f"✨ Buat Draf Awal {bab_name}", key=f"gen_{bab_name}"):
                    with st.spinner(f"AI sedang merangkai narasi natural untuk {bab_name}..."):
                        try:
                            user_prompt = f"Tuliskan draf teks ilmiah untuk '{bab_name}' secara lengkap, komprehensif, dan mendalam terkait judul: '{st.session_state.riset['Topik']}'."
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=user_prompt,
                                config=types.GenerateContentConfig(system_instruction=base_instruction)
                            )
                            st.session_state.riset[bab_name] = response.text
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {e}")
            
            # FITUR UTAMA: Hub Umpan Balik Agar AI Belajar & Memperbaiki Diri Secara Real-Time
            else:
                st.subheader(f"🛠️ Ajarkan AI Cara Memperbaiki {bab_name} (Human-in-the-Loop)")
                evaluasi_teks = st.text_area(
                    "Kritik & Berikan Arahan Manusia (Apa yang kurang natural dari teks di atas?):",
                    placeholder="Contoh: 'Paragraf kedua terlalu teoritis dan kaku, ubah narasinya agar lebih menonjolkan analisis etnopedagogi di lapangan secara praktis.'",
                    key=f"eval_{bab_name}"
                )
                
                if st.button(f"Ajarkan AI & Perbarui {bab_name} 🚀", key=f"btn_{bab_name}"):
                    if evaluasi_teks:
                        # Masukkan kritik ke memori jangka panjang aplikasi agar bab berikutnya ikut pintar
                        st.session_state.ai_learning_logs.append(f"- Pada {bab_name}: {evaluasi_teks}")
                        
                        with st.spinner("AI sedang menyerap evaluasi Anda dan menulis ulang..."):
                            try:
                                response = client.models.generate_content(
                                    model='gemini-2.5-flash',
                                    contents=f"Kritik Pengguna:\n{evaluasi_teks}",
                                    config=types.GenerateContentConfig(
                                        system_instruction=f"Anda adalah Profesor Ahli. Perbaiki teks asli berikut agar lebih humanis, tajam, dan mengalir mengikuti kritik dari pengguna secara mutlak.\n\nTeks Asli:\n\n{st.session_state.riset[bab_name]}"
                                    )
                                )
                                st.session_state.riset[bab_name] = response.text
                                st.success("AI Berhasil Belajar! Teks diperbarui dengan gaya bahasa yang disempurnakan.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal: {e}")

# Tab Daftar Pustaka Bawaan
with tabs[5]:
    st.header("📚 Generator Daftar Pustaka")
    if st.button("Generate Format APA 🔄"):
        st.session_state.references_pool = [
            {"authors": "Kurniawan, I. U.", "year": "2026", "title": "Kebijakan Literasi Berbasis Etnopedagogi", "journal": "Jurnal Pendidikan dan Kebudayaan", "volume": "15", "issue": "1", "pages": "45-58"}
        ]
        for ref in st.session_state.references_pool:
            st.markdown(f"{ref['authors']} ({ref['year']}). {ref['title']}. *{ref['journal']}*, {ref['volume']}({ref['issue']}), {ref['pages']}.")

# Tab Unduh Dokumen
with tabs[6]:
    st.header("💾 Ekspor Manuskrip")
    full_manuscript = f"JUDUL: {st.session_state.riset['Topik']}\n\n"
    for bab, content in st.session_state.riset.items():
        if bab != "Topik": full_manuscript += f"=== {bab} ===\n\n{content}\n\n"
    st.download_button(label="📥 Unduh File Word/Google Docs (.doc)", data=full_manuscript, file_name="Riset_Adaptive.doc", mime="application/msword")
