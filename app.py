import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="Academic Copilot Data Pro", page_icon="🎓", layout="wide")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Inisialisasi struktur memori aplikasi
if "riset" not in st.session_state:
    st.session_state.riset = {
        "Topik": "",
        "Bab 1: Pendahuluan": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 2: Tinjauan Pustaka": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 3: Metodologi Penelitian": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 4: Pembahasan & Analisis": "Belum dibuat. Klik tombol di bawah untuk mulai.",
        "Bab 5: Kesimpulan & Referensi": "Belum dibuat. Klik tombol di bawah untuk mulai."
    }

with st.sidebar:
    st.header("⚙️ Papan Kendali Proyek")
    topik_input = st.text_input("Fokus Topik / Judul Karya Ilmiah:", placeholder="Masukkan topik riset...")
    
    if st.button("Kunci Judul Proyek 🔒", type="primary"):
        if topik_input:
            st.session_state.riset["Topik"] = topik_input
            st.rerun()

    st.write("---")
    st.header("📁 Unggah Dokumen & Data")
    
    # Fitur 1: Mengunggah template dokumen/gaya selingkung
    uploaded_template = st.file_uploader("Unggah Contoh Dokumen / Template Acuan (.txt)", type=["txt"])
    template_context = ""
    if uploaded_template is not None:
        template_context = uploaded_template.read().decode("utf-8")
        st.success("Template berhasil dibaca!")

    # Fitur 2: Mengunggah data empiris hasil penelitian
    uploaded_data = st.file_uploader("Unggah Data Empiris / Hasil Penelitian (.txt)", type=["txt"])
    data_context = ""
    if uploaded_data is not None:
        data_context = uploaded_data.read().decode("utf-8")
        st.success("Data empiris berhasil dimuat!")

st.title("🎓 Academic AI Copilot — Workspace Modular Data-Driven")

if st.session_state.riset["Topik"]:
    st.subheader(f"📁 Proyek Aktif: {st.session_state.riset['Topik']}")
else:
    st.info("👋 Silakan masukkan topik di sidebar, lalu kunci proyek untuk memulai.")

tabs = st.tabs(["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

# Mengatur instruksi dasar AI agar adaptif terhadap file yang diunggah
base_instruction = (
    "Anda adalah Senior Research Professor. Tulis draf ilmiah formal yang sangat panjang, mendalam, dan substantif. "
    "JANGAN MENULIS RINGKASAN."
)
if template_context:
    base_instruction += f"\n\n[PENTING] Anda WAJIB meniru gaya bahasa, struktur penulisan, dan format dokumen dari template berikut ini:\n{template_context}"

for i, bab_name in enumerate(list(st.session_state.riset.keys())[1:]):
    with tabs[i]:
        st.header(bab_name)
        st.markdown(st.session_state.riset[bab_name])
        st.markdown("---")
        
        if st.session_state.riset["Topik"]:
            if "Belum dibuat" in st.session_state.riset[bab_name]:
                if st.button(f"✨ Buat Draf Awal {bab_name}", key=f"gen_{bab_name}"):
                    with st.spinner(f"Menyusun {bab_name}..."):
                        try:
                            # Menambahkan data empiris khusus saat menyusun Bab 4 (Pembahasan)
                            user_prompt = f"Tuliskan {bab_name} secara komprehensif untuk penelitian berjudul '{st.session_state.riset['Topik']}'."
                            if "Bab 4" in bab_name and data_context:
                                user_prompt += f"\n\nBerikut adalah data empiris hasil penelitian di lapangan yang WAJIB Anda olah, analisis, dan narasikan ke dalam pembahasan:\n{data_context}"
                            
                            response = client.chat.completions.create(
                                model="gemini-2.5-flash", # <--- Ganti nama model terbaru di sini jika diperlukan
                                messages=[
                                    {"role": "system", "content": base_instruction},
                                    {"role": "user", "content": user_prompt}
                                ]
                            )
                            st.session_state.riset[bab_name] = response.choices[0].message.content
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {e}")
            
            # Hub Revisi Terbimbing
            else:
                st.subheader(f"🛠️ Hub dan Perintah Revisi ({bab_name})")
                instruksi_revisi = st.text_area(f"Ketik perintah spesifik untuk menyempurnakan {bab_name}:", key=f"input_{bab_name}")
                
                if st.button(f"Kembangkan & Revisi {bab_name} 🚀", key=f"btn_{bab_name}"):
                    if instruksi_revisi:
                        with st.spinner("Merevisi..."):
                            try:
                                # Jika ada data empiris baru, ikut sertakan dalam proses revisi
                                konteks_tambahan = f"\nData empiris yang tersedia:\n{data_context}" if data_context else ""
                                response = client.chat.completions.create(
                                    model="gemini-2.5-flash", # <--- Ganti nama model terbaru di sini jika diperlukan
                                    messages=[
                                        {"role": "system", "content": "Anda adalah Profesor Ahli. Lakukan revisi mendalam pada draf teks ilmiah berdasarkan instruksi pengguna."},
                                        {"role": "user", "content": f"Teks Asli:\n\n{st.session_state.riset[bab_name]}{konteks_tambahan}"},
                                        {"role": "user", "content": f"Perintah Perubahan:\n\n{instruksi_revisi}"}
                                    ]
                                )
                                st.session_state.riset[bab_name] = response.choices[0].message.content
                                st.success("Berhasil diperbarui!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal: {e}")
