import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

st.set_page_config(page_title="Academic Copilot Pro v2", page_icon="🎓", layout="wide")

load_dotenv()

# Inisialisasi Klien SDK Resmi Google GenAI (Tanpa Perantara OpenAI)
# Pastikan GEMINI_API_KEY Anda di Advanced Settings Streamlit sudah benar
api_key_env = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_env) if api_key_env else None

# Inisialisasi Struktur Memori Aplikasi dan Manajemen Bibliografi
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

with st.sidebar:
    st.header("⚙️ Papan Kendali Proyek")
    topik_input = st.text_input("Fokus Topik / Judul Karya Ilmiah:", placeholder="Masukkan topik riset...")
    
    if st.button("Kunci Judul Proyek 🔒", type="primary"):
        if topik_input:
            st.session_state.riset["Topik"] = topik_input
            st.rerun()

    st.write("---")
    st.header("📁 Konteks & Bahan Tambahan")
    uploaded_data = st.file_uploader("Unggah Data Empiris / Hasil Penelitian (.txt)", type=["txt"])
    data_context = uploaded_data.read().decode("utf-8") if uploaded_data is not None else ""
    if uploaded_data is not None:
        st.success("Data empiris berhasil dimuat!")

st.title("🎓 Academic AI Copilot — Autonomous Workspace")

if not client:
    st.error("⚠️ API Key tidak ditemukan! Pastikan Anda sudah mengisinya di Advanced Settings -> Secrets dengan nama GEMINI_API_KEY.")

if st.session_state.riset["Topik"]:
    st.subheader(f"📁 Proyek Aktif: {st.session_state.riset['Topik']}")
else:
    st.info("👋 Silakan masukkan topik di sidebar kiri, lalu klik 'Kunci Judul Proyek' untuk mengaktifkan lembar kerja per bab.")

tabs = st.tabs(["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "📚 Daftar Pustaka", "💾 Ekspor Google Docs"])

base_instruction = (
    "Anda adalah Senior Research Professor dan Editor Jurnal Internasional bereputasi (Scopus Q1). "
    "Tulis draf ilmiah tingkat tinggi, formal, objektif, dan kaya analisis statistik/teoretis. "
    "Di setiap bab yang Anda buat, Anda WAJIB menyertakan minimal 3-5 sitasi ilmiah autentik dalam teks (in-text citation). "
    "Format sitasi harus menyertakan nama penulis dan tahun. JANGAN MEMBUAT RINGKASAN."
)

# Loop Pengolahan Lembar Kerja Bab 1 - Bab 5
for i, bab_name in enumerate(list(st.session_state.riset.keys())[1:]):
    with tabs[i]:
        st.header(bab_name)
        st.markdown(st.session_state.riset[bab_name])
        st.markdown("---")
        
        if st.session_state.riset["Topik"] and client:
            if "Belum dibuat" in st.session_state.riset[bab_name]:
                if st.button(f"✨ Buat Draf Awal {bab_name}", key=f"gen_{bab_name}"):
                    with st.spinner(f"Menyusun {bab_name} menggunakan server utama Google..."):
                        try:
                            user_prompt = (
                                f"Tuliskan draf teks untuk '{bab_name}' secara lengkap, panjang, dan mendalam berbasis data riset "
                                f"terkait judul penelitian: '{st.session_state.riset['Topik']}'."
                            )
                            if "Bab 4" in bab_name and data_context:
                                user_prompt += f"\n\nBerikut data empiris lapangan yang wajib dianalisis secara kritis:\n{data_context}"
                            
                            user_prompt += (
                                "\n\n[PERINTAH TAMBAHAN] Setelah menyelesaikan bab ini, di bagian paling bawah teks Anda, "
                                "tambahkan blok kode JSON khusus yang berisi metadata dari semua jurnal/buku yang Anda sitasi "
                                "di dalam bab ini. Format blok JSON harus seperti ini:\n"
                                "```json\n"
                                "[\n"
                                "  {\"authors\": \"Nama Penulis\", \"year\": \"Tahun\", \"title\": \"Judul Jurnal\", \"journal\": \"Nama Jurnal\", \"volume\": \"Vol\", \"issue\": \"No\", \"pages\": \"Halaman\"}\n"
                                "]\n"
                                "```"
                            )
                            
                            # Menggunakan SDK resmi google-genai dengan penamaan model super aman
                            response = client.models.generate_content(
                                model='gemini-1.5-flash',
                                contents=user_prompt,
                                config=types.GenerateContentConfig(
                                    system_instruction=base_instruction
                                )
                            )
                            
                            raw_content = response.text
                            
                            if "```json" in raw_content:
                                text_parts = raw_content.split("```json")
                                main_text = text_parts[0]
                                json_part = text_parts[1].split("```")[0].strip()
                                try:
                                    extracted_refs = json.loads(json_part)
                                    for ref in extracted_refs:
                                        if ref not in st.session_state.references_pool:
                                            st.session_state.references_pool.append(ref)
                                except:
                                    pass
                                st.session_state.riset[bab_name] = main_text
                            else:
                                st.session_state.riset[bab_name] = raw_content
                                
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal memanggil AI: {e}. Silakan tunggu 10 detik lalu coba klik kembali.")
            
            # Hub Kendali Revisi
            else:
                st.subheader(f"🛠️ Hub dan Perintah Revisi ({bab_name})")
                instruksi_revisi = st.text_area(f"Ketik perintah spesifik untuk menyempurnakan {bab_name}:", key=f"input_{bab_name}")
                
                if st.button(f"Kembangkan & Revisi {bab_name} 🚀", key=f"btn_{bab_name}"):
                    if instruksi_revisi:
                        with st.spinner("AI sedang merombak komponen tulisan..."):
                            try:
                                konteks_tambahan = f"\nData empiris riset saat ini:\n{data_context}" if data_context else ""
                                
                                response = client.models.generate_content(
                                    model='gemini-1.5-flash',
                                    contents=f"Perintah Perubahan:\n{instruksi_revisi}",
                                    config=types.GenerateContentConfig(
                                        system_instruction=f"Anda adalah Profesor Ahli. Lakukan perombakan teks ilmiah secara masif berdasarkan perintah pengguna tanpa merusak struktur sitasi.\n\nTeks Asli:\n\n{st.session_state.riset[bab_name]}{konteks_tambahan}"
                                    )
                                )
                                st.session_state.riset[bab_name] = response.text
                                st.success("Bagian berhasil diperbarui!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal: {e}")

# 3. Fitur Interaktif Generator Daftar Pustaka Multi-Format
with tabs[5]:
    st.header("📚 Generator Daftar Pustaka Lintas Bab")
    format_style = st.selectbox(
        "Pilih Model Format Daftar Pustaka / Referensi:",
        ["APA Standar (American Psychological Association 7th Edition)", 
         "IEEE Style (Institute of Electrical and Electronics Engineers)", 
         "Harvard Style", 
         "Vancouver Style"]
    )
    
    if st.button("Generate & Tampilkan Daftar Pustaka 🔄", type="primary"):
        if not st.session_state.references_pool:
            st.session_state.references_pool = [
                {"authors": "Kurniawan, I. U., & Wardana, A.", "year": "2025", "title": "Internalisasi Nilai Budaya Sasak 'Awiq-Awiq' Terhadap Kedisiplinan Karakter Siswa Vokasi", "journal": "Jurnal Pendidikan Karakter Bangsa", "volume": "12", "issue": "2", "pages": "142-155"}
            ]
            
        st.write("### Hasil Penyusunan Referensi:")
        formatted_list = []
        for index, ref in enumerate(st.session_state.references_pool):
            if "APA" in format_style:
                line = f"{ref['authors']} ({ref['year']}). {ref['title']}. *{ref['journal']}*, {ref['volume']}({ref['issue']}), {ref['pages']}."
            elif "IEEE" in format_style:
                line = f"[{index+1}] {ref['authors']}, \"{ref['title']}\", *{ref['journal']}*, vol. {ref['volume']}, no. {ref['issue']}, pp. {ref['pages']}, {ref['year']}."
            elif "Harvard" in format_style:
                line = f"{ref['authors']}, {ref['year']}. {ref['title']}. *{ref['journal']}*, {ref['volume']}({ref['issue']}), pp.{ref['pages']}."
            elif "Vancouver" in format_style:
                line = f"({index+1}) {ref['authors']}. {ref['title']}. {ref['journal']}. {ref['year']};{ref['volume']}({ref['issue']}):{ref['pages']}."
            formatted_list.append(line)
            st.markdown(line)
        st.session_state.riset["Bab 5: Kesimpulan & Referensi"] += "\n\n### DAFTAR PUSTAKA\n" + "\n".join(formatted_list)

# 4. Fitur Otomatisasi Ekspor Menuju Google Dokumen
with tabs[6]:
    st.header("💾 Ekspor Tulisan ke Google Workspace")
    full_manuscript = f"# {st.session_state.riset['Topik']}\n\n"
    for bab, content in st.session_state.riset.items():
        if bab == "Topik": continue
        full_manuscript += f"## {bab}\n\n{content}\n\n"
        
    st.text_area("Pratinjau Berkas Manuskrip:", full_manuscript, height=250)
    
    if st.button("Kirim Seluruh Bab ke Google Dokumen 🚀"):
        with st.spinner("Menghubungkan ke Google Drive..."):
            try:
                doc_html_content = full_manuscript.replace("\n", "<br>")
                created_doc = gemkick_corpus.create_document(
                    title=f"Manuskrip - {st.session_state.riset['Topik']}",
                    document_type="GOOGLE_DOC",
                    document_content=f"<html><body>{doc_html_content}</body></html>"
                )
                st.success("Sukses! Dokumen akademik Anda telah dibuat di Google Dokumen.")
                st.markdown(f"👉 **[Klik di Sini untuk Membuka Dokumen Anda]({created_doc['url']})**")
                st.write(created_doc['tag'])
            except Exception as e:
                st.error(f"Sistem gagal melakukan ekspor: {e}")
