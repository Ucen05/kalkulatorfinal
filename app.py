import streamlit as st
import sympy as sp
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Config Halaman Utama
st.set_page_config(page_title="Kalkulator Komparasi Tiga Metode", layout="wide")

# 1. Header Aplikasi
st.title("🧮 Kalkulator & Komparasi Tiga Metode Persamaan Non-Linier")
st.write("""
Aplikasi ini membandingkan **Metode Biseksi**, **Metode Newton-Raphson**, dan **Metode Secant** 
secara visual, akurat, serta mendukung ekspor data log iterasi ke dalam format CSV/Excel.
""")
st.markdown("---")

# Layout: Kiri (Input), Kanan (Hasil)
kolom_input, kolom_hasil = st.columns([1.1, 2.3], gap="large")

with kolom_input:
    st.subheader("⚙️ Langkah 1: Masukkan Parameter")
    
    # 1. Input Fungsi Bersama
    with st.expander("📌 1. Input Fungsi f(x)", expanded=True):
        # Tambahkan instruksi visual yang langsung terlihat oleh pengguna
        st.info("💡 **Aturan Penulisan Pangkat & Perkalian:**\n*   Pangkat menggunakan **bintang dua** (Contoh $x^2$ ditulis: `x**2`)\n*   Perkalian wajib menggunakan **bintang satu** (Contoh $3x$ ditulis: `3*x`) ")
        
        fungsi_input = st.text_input(
            "Masukkan Persamaan Fungsi:", 
            value="x**3 - x - 2"
        )

    # 2. Parameter Biseksi
    with st.expander("🔍 2. Parameter Metode Biseksi", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            a_input = st.number_input("Batas Bawah (a):", value=1.0, format="%.4f")
        with col_b:
            b_input = st.number_input("Batas Atas (b):", value=2.0, format="%.4f")
        st.caption("⚠️ *Syarat: f(a) dan f(b) tandanya harus berlawanan.*")

    # 3. Parameter Newton-Raphson
    with st.expander("⚡ 3. Parameter Newton-Raphson", expanded=True):
        x0_nr = st.number_input("Tebakan Awal (x0) NR:", value=2.0, format="%.4f", key="nr_x0")
        st.caption("ℹ️ *Butuh 1 tebakan awal dan otomatis mencari turunan f'(x).*")

    # 4. Parameter Secant
    with st.expander("📐 4. Parameter Metode Secant", expanded=True):
        col_x0, col_x1 = st.columns(2)
        with col_x0:
            x0_sec = st.number_input("Tebakan Awal 1 (x0):", value=1.0, format="%.4f", key="sec_x0")
        with col_x1:
            x1_sec = st.number_input("Tebakan Awal 2 (x1):", value=2.0, format="%.4f", key="sec_x1")
        st.caption("ℹ️ *Butuh 2 tebakan awal, bebas tidak terikat syarat tanda berlawanan.*")

    # 5. Kriteria Henti
    with st.expander("🛑 5. Kriteria Batasan (Henti)", expanded=False):
        tol = st.number_input("Toleransi Target Error:", value=0.001, format="%.5f", step=0.0001)
        max_iter = st.number_input("Maksimal Batas Iterasi:", value=50, step=1)

    st.markdown("###")
    TOMBOL_HITUNG = st.button("🚀 JALANKAN KOMPARASI TRIFECTA", use_container_width=True, type="primary")

with kolom_hasil:
    st.subheader("📊 Langkah 2: Analisis Hasil")
    
    if TOMBOL_HITUNG:
        x = sp.symbols('x')
        
        try:
            ekspresi = sp.sympify(fungsi_input)
            f = sp.lambdify(x, ekspresi, "numpy")
            
            ringkasan_data = []
            
            # ----------------------------------------------------
            # PERHITUNGAN 1: BISEKSI
            # ----------------------------------------------------
            biseksi_sukses = False
            biseksi_akar = None
            df_biseksi = pd.DataFrame()
            biseksi_pesan_error = ""
            
            if f(a_input) * f(b_input) >= 0:
                biseksi_pesan_error = f"f(a)={f(a_input):.2f} dan f(b)={f(b_input):.2f} tandanya sama."
                ringkasan_data.append(["Metode Biseksi", "-", "-", f"❌ Gagal: {biseksi_pesan_error}"])
            else:
                data_biseksi = []
                iterasi = 1
                error_hitung = 1.0
                a, b = a_input, b_input
                c_lama = a
                
                while iterasi <= max_iter:
                    c = (a + b) / 2
                    fc = f(c)
                    
                    if iterasi > 1:
                        error_hitung = abs((c - c_lama) / c)
                        error_tampilan = f"{error_hitung:.6f}"
                    else:
                        error_hitung = 999.0
                        error_tampilan = "-"
                        
                    data_biseksi.append([iterasi, f"{a:.6f}", f"{b:.6f}", f"{c:.6f}", f"{f(a):.6f}", f"{f(b):.6f}", f"{fc:.6f}", error_tampilan])
                    
                    if iterasi > 1 and error_hitung <= tol:
                        break
                        
                    if f(a) * fc < 0:
                        b = c
                    else:
                        a = c
                        
                    c_lama = c
                    iterasi += 1
                
                biseksi_sukses = True
                biseksi_akar = c_lama
                df_biseksi = pd.DataFrame(data_biseksi, columns=["Iterasi", "a", "b", "c (Akar)", "f(a)", "f(b)", "f(c)", "Error Relatif"])
                ringkasan_data.append(["Metode Biseksi", f"{biseksi_akar:.6f}", f"{len(data_biseksi)} Kali", "✅ Sukses"])

            # ----------------------------------------------------
            # PERHITUNGAN 2: NEWTON-RAPHSON
            # ----------------------------------------------------
            nr_sukses = False
            nr_akar = None
            df_nr = pd.DataFrame()
            
            turunan_ekspresi = sp.diff(ekspresi, x)
            f_prime = sp.lambdify(x, turunan_ekspresi, "numpy")
            
            data_nr = []
            xn = x0_nr
            iterasi_nr = 1
            konvergen_nr = False
            nr_pembagian_nol = False
            
            while iterasi_nr <= max_iter:
                fxn = f(xn)
                fpxn = f_prime(xn)
                
                if fpxn == 0:
                    nr_pembagian_nol = True
                    break
                    
                xn_baru = xn - (fxn / fpxn)
                error_nr = abs((xn_baru - xn) / xn_baru) if xn_baru != 0 else 0
                
                data_nr.append([iterasi_nr, f"{xn:.6f}", f"{fxn:.6f}", f"{fpxn:.6f}", f"{xn_baru:.6f}", f"{error_nr:.6f}"])
                
                if error_nr <= tol:
                    xn = xn_baru
                    konvergen_nr = True
                    break
                    
                xn = xn_baru
                iterasi_nr += 1
            
            if nr_pembagian_nol:
                ringkasan_data.append(["Newton-Raphson", "-", "-", "❌ Gagal: Turunan f'(x) = 0"])
            elif konvergen_nr:
                nr_sukses = True
                nr_akar = xn
                df_nr = pd.DataFrame(data_nr, columns=["Iterasi", "xn", "f(xn)", "f'(xn)", "xn+1", "Error Relatif"])
                ringkasan_data.append(["Newton-Raphson", f"{nr_akar:.6f}", f"{iterasi_nr} Kali", "⚡ Sukses (Cepat)"])
            else:
                df_nr = pd.DataFrame(data_nr, columns=["Iterasi", "xn", "f(xn)", "f'(xn)", "xn+1", "Error Relatif"])
                ringkasan_data.append(["Newton-Raphson", f"{xn:.6f}", f"{max_iter} Kali", "⚠️ Batas Habis"])

            # ----------------------------------------------------
            # PERHITUNGAN 3: SECANT
            # ----------------------------------------------------
            sec_sukses = False
            sec_akar = None
            df_sec = pd.DataFrame()
            sec_pembagian_nol = False
            
            data_sec = []
            x_min1 = x0_sec
            x_0 = x1_sec
            iterasi_sec = 1
            konvergen_sec = False
            
            while iterasi_sec <= max_iter:
                fx_min1 = f(x_min1)
                fx_0 = f(x_0)
                
                if (fx_0 - fx_min1) == 0:
                    sec_pembagian_nol = True
                    break
                
                x_baru = x_0 - (fx_0 * (x_0 - x_min1)) / (fx_0 - fx_min1)
                error_sec = abs((x_baru - x_0) / x_baru) if x_baru != 0 else 0
                fx_baru = f(x_baru)
                
                data_sec.append([iterasi_sec, f"{x_min1:.6f}", f"{x_0:.6f}", f"{x_baru:.6f}", f"{fx_min1:.6f}", f"{fx_0:.6f}", f"{fx_baru:.6f}", f"{error_sec:.6f}"])
                
                if error_sec <= tol:
                    sec_akar = x_baru
                    konvergen_sec = True
                    break
                    
                x_min1 = x_0
                x_0 = x_baru
                iterasi_sec += 1
                
            if sec_pembagian_nol:
                ringkasan_data.append(["Metode Secant", "-", "-", "❌ Gagal: Pembagian dengan Nol"])
            elif konvergen_sec:
                sec_sukses = True
                df_sec = pd.DataFrame(data_sec, columns=["Iterasi", "x_n-1", "x_n", "x_n+1 (Akar)", "f(x_n-1)", "f(x_n)", "f(x_n+1)", "Error Relatif"])
                ringkasan_data.append(["Metode Secant", f"{sec_akar:.6f}", f"{iterasi_sec} Kali", "🚀 Sukses"])
            else:
                df_sec = pd.DataFrame(data_sec, columns=["Iterasi", "x_n-1", "x_n", "x_n+1 (Akar)", "f(x_n-1)", "f(x_n)", "f(x_n+1)", "Error Relatif"])
                ringkasan_data.append(["Metode Secant", f"{x_0:.6f}", f"{max_iter} Kali", "⚠️ Batas Habis"])


            # ----------------------------------------------------
            # VISUALISASI OUTPUT KESELURUHAN
            # ----------------------------------------------------
            # Poin 1: Tabel Ringkasan Presisi (6 desimal seragam)
            st.markdown("#### 🏆 Kesimpulan Perbandingan Kecepatan (3 Metode)")
            df_ringkasan = pd.DataFrame(ringkasan_data, columns=["Metode Numerik", "Akar Persamaan (x)", "Jumlah Iterasi", "Status Eksekusi"])
            st.dataframe(df_ringkasan, hide_index=True, use_container_width=True)
            
            # 2. Grafik Bersama
            st.markdown("#### 📈 Letak Akar pada Grafik Fungsi")
            akar_referensi = biseksi_akar if biseksi_sukses else (nr_akar if nr_sukses else x1_sec)
            x_vals = np.linspace(akar_referensi - 3, akar_referensi + 3, 500)
            y_vals = f(x_vals)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Kurva f(x)', line=dict(color='#1f77b4', width=2.5)))
            fig.add_shape(type="line", x0=min(x_vals), y0=0, x1=max(x_vals), y1=0, line=dict(color="black", width=1, dash="dash"))
            
            if biseksi_sukses:
                fig.add_trace(go.Scatter(x=[biseksi_akar], y=[0], mode='markers', name='Akar Biseksi', marker=dict(color='#2ca02c', size=12, symbol='circle')))
            if nr_sukses:
                fig.add_trace(go.Scatter(x=[nr_akar], y=[0], mode='markers', name='Akar Newton-Raphson', marker=dict(color='#d62728', size=10, symbol='x')))
            if sec_sukses:
                fig.add_trace(go.Scatter(x=[sec_akar], y=[0], mode='markers', name='Akar Secant', marker=dict(color='#ff7f0e', size=10, symbol='diamond')))
                
            fig.update_layout(xaxis_title="Sumbu X", yaxis_title="Sumbu Y / f(x)", hovermode="x unified", height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

            # 3. Log Detail Tiap Metode (Poin 2: Struktur Kolom Secant Dioptimalkan)
            st.markdown("#### 📋 Log Langkah Perhitungan Berdasarkan Tabel")
            tab1, tab2, tab3 = st.tabs(["🔍 Detail Biseksi", "⚡ Detail Newton-Raphson", "📐 Detail Secant"])
            
            with tab1:
                if biseksi_sukses:
                    st.dataframe(df_biseksi, hide_index=True, use_container_width=True)
                    st.download_button(label="📥 Unduh Hasil Iterasi Biseksi (CSV)", data=df_biseksi.to_csv(index=False).encode('utf-8'), file_name='iterasi_biseksi.csv', mime='text/csv', key='download_biseksi')
                else:
                    st.error(f"Gagal: {biseksi_pesan_error}")
                    
            with tab2:
                if not df_nr.empty:
                    st.info(f"💡 **Info Sistem:** Turunan otomatis $f'(x)$ dideteksi: `{turunan_ekspresi}`")
                    st.dataframe(df_nr, hide_index=True, use_container_width=True)
                    st.download_button(label="📥 Unduh Hasil Iterasi Newton-Raphson (CSV)", data=df_nr.to_csv(index=False).encode('utf-8'), file_name='iterasi_newton_raphson.csv', mime='text/csv', key='download_nr')
                elif nr_pembagian_nol:
                    st.error("Gagal: Terjadi pembagian dengan nol pada f'(x)=0.")
                    
            with tab3:
                if sec_sukses:
                    st.dataframe(df_sec, hide_index=True, use_container_width=True)
                    st.download_button(label="📥 Unduh Hasil Iterasi Secant (CSV)", data=df_sec.to_csv(index=False).encode('utf-8'), file_name='iterasi_secant.csv', mime='text/csv', key='download_secant')
                elif sec_pembagian_nol:
                    st.error("Gagal: Terjadi pembagian nol karena nilai f(x_n) dan f(x_n-1) sama.")
                else:
                    st.warning("Data kosong.")
                    
        except Exception as e:
            st.error(f"⚠️ Pola penulisan fungsi matematika tidak valid. Mohon periksa kembali input Anda. Detail: {e}")
            
    else:
        st.info("💡 Silakan atur parameter di kolom sebelah kiri, lalu klik tombol 'JALANKAN KOMPARASI TRIFECTA' untuk melihat hasil perbandingan tiga metode.")

# ----------------------------------------------------
# Poin 3: Tambahan Dokumentasi Teori di Bagian Paling Bawah
# ----------------------------------------------------
st.markdown("---")
with st.expander("📖 Pustaka Rumus & Teori Singkat (Bahan Contekan Presentasi)", expanded=False):
    st.markdown("""
    ### 1. Metode Biseksi (Bisection)
    Metode pengurungan akar (bracketing method) dengan membagi dua interval secara kontinu.
    *   **Rumus Titik Tengah:** $c = \\frac{a + b}{2}$
    *   **Kondisi Iterasi:** Jika $f(a) \\times f(c) < 0$, maka batas atas baru adalah $b = c$. Jika tidak, batas bawah baru adalah $a = c$.

    ### 2. Metode Newton-Raphson
    Metode terbuka berbasis pendekatan garis singgung (turunan) di titik tebakan terdekat.
    *   **Rumus Utama:** $x_{n+1} = x_n - \\frac{f(x_n)}{f'(x_n)}$
    *   *Kelemahan:* Mengalami kegagalan fungsi jika di tengah jalan nilai turunan $f'(x_n) = 0$ (pembagian dengan nol).

    ### 3. Metode Secant
    Metode terbuka yang memodifikasi Newton-Raphson dengan cara mengganti fungsi turunan $f'(x_n)$ menggunakan gradien garis miring berdasarkan dua titik tebakan awal.
    *   **Rumus Utama:** $x_{n+1} = x_n - \\frac{f(x_n)(x_n - x_{n-1})}{f(x_n) - f(x_{n-1})}$
    """)