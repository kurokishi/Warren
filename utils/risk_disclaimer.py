class RiskDisclaimer:
    """Centralized risk disclaimer for predictions"""
    
    @staticmethod
    def get_price_prediction_disclaimer():
        return {
            'title': '⚠️ PERINGATAN RISIKO PREDIKSI HARGA',
            'content': '''
            **INFORMASI PENTING UNTUK SEMUA PENGGUNA:**
            
            1. **BUKAN JAMINAN:** Prediksi harga adalah estimasi probabilistik, bukan jaminan.
            2. **AKURASI TERBATAS:** Akurasi prediksi harga saham maksimal 50-60% dalam kondisi terbaik.
            3. **FAKTOR EKSTERNAL:** Tidak memperhitungkan berita mendadak, geopolitik, atau intervensi regulator.
            4. **VOLATILITAS:** Pasar saham Indonesia memiliki volatilitas tinggi yang sulit diprediksi.
            5. **KEWAJIBAN ANDA:** Anda bertanggung jawab penuh atas keputusan investasi.
            
            **REKOMENDASI KAMI:**
            - Gunakan prediksi sebagai salah satu dari banyak alat analisis
            - Prioritaskan analisis fundamental jangka panjang
            - Diversifikasi portofolio untuk mengurangi risiko
            - Konsultasi dengan penasihat keuangan tersertifikasi
            ''',
            'acceptance_required': True
        }
    
    @staticmethod
    def get_trading_scenario_disclaimer():
        return {
            'title': '📊 PENJELASAN SKENARIO TRADING',
            'content': '''
            **CARA MEMAKAI SKENARIO TRADING:**
            
            1. **Probabilitas:** Angka persentase adalah estimasi, bukan kepastian.
            2. **Multiple Scenarios:** Selalu pertimbangkan semua skenario, bukan hanya satu.
            3. **Risk Management:** Tentukan posisi size berdasarkan risiko maksimal 1-2% dari modal per trade.
            4. **Confirmation:** Tunggu konfirmasi teknis sebelum eksekusi.
            5. **Exit Plan:** Tentukan exit point (TP/SL) SEBELUM masuk posisi.
            
            **CONTOH PENGGUNAAN AMAN:**
            - Modal: Rp 100,000,000
            - Risk per trade: 1% = Rp 1,000,000
            - Stop Loss: 5% dari entry
            - Position Size: Rp 1,000,000 / 5% = Rp 20,000,000
            ''',
            'acceptance_required': False
        }
