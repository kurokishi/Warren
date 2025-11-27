class ComplianceEngine:
    """
    Generates regulatory-safe disclaimers for AI stock analysis.
    """

    BASE_DISCLAIMER = (
        "Analisis ini dihasilkan oleh sistem AI sebagai alat bantu riset. "
        "Bukan merupakan rekomendasi investasi, ajakan membeli atau menjual "
        "efek tertentu. Investor bertanggung jawab penuh atas setiap "
        "keputusan investasi yang diambil."
    )

    RISK_NOTE = (
        "Investasi saham mengandung risiko, termasuk kemungkinan "
        "kehilangan sebagian atau seluruh modal."
    )

    def generate(self, context: dict | None = None) -> str:
        """
        Context can include: market, user_type, horizon
        """
        disclaimer = self.BASE_DISCLAIMER

        if context:
            if context.get("horizon") == "short":
                disclaimer += (
                    " Analisis ini tidak dirancang untuk transaksi "
                    "jangka sangat pendek atau aktivitas spekulatif."
                )

            if context.get("user_type") == "retail":
                disclaimer += (
                    " Informasi ini bersifat umum dan tidak "
                    "mempertimbangkan tujuan, profil risiko, "
                    "ataupun kondisi keuangan pribadi investor."
                )

        disclaimer += f" {self.RISK_NOTE}"
        return disclaimer
