import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PeerComparator:
    """
    Compare stocks within the same sector/industry
    """
    
    # Mapping ticker to sector (sederhana, bisa dikembangkan)
    SECTOR_MAP = {
        'BBCA.JK': 'Banking',
        'BBRI.JK': 'Banking',
        'BMRI.JK': 'Banking',
        'TLKM.JK': 'Telecom',
        'EXCL.JK': 'Telecom',
        'ASII.JK': 'Automotive',
        'AUTO.JK': 'Automotive',
        'UNVR.JK': 'Consumer',
        'ICBP.JK': 'Consumer',
        'INDF.JK': 'Consumer',
        'ANTM.JK': 'Mining',
        'PTBA.JK': 'Mining',
        'ADRO.JK': 'Mining',
        'JSMR.JK': 'Infrastructure',
        'WIKA.JK': 'Infrastructure',
        'PGAS.JK': 'Energy',
    }
    
    def __init__(self):
        self.peer_groups = {
            'Banking': ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BNII.JK', 'BBNI.JK'],
            'Telecom': ['TLKM.JK', 'EXCL.JK', 'ISAT.JK', 'FREN.JK'],
            'Consumer': ['UNVR.JK', 'ICBP.JK', 'INDF.JK', 'MYOR.JK', 'ULTJ.JK'],
            'Mining': ['ANTM.JK', 'PTBA.JK', 'ADRO.JK', 'ITMG.JK', 'MDKA.JK'],
            'Property': ['BSDE.JK', 'CTRA.JK', 'PWON.JK', 'LPKR.JK'],
            'Infrastructure': ['JSMR.JK', 'WIKA.JK', 'PTPP.JK', 'WSKT.JK']
        }
    
    def get_sector_peers(self, ticker: str) -> list:
        """Get peers in the same sector"""
        sector = self.SECTOR_MAP.get(ticker)
        if sector and sector in self.peer_groups:
            # Remove the ticker itself from peers
            peers = [p for p in self.peer_groups[sector] if p != ticker]
            return peers[:4]  # Return max 4 peers
        return []
    
    def create_comparison_data(self, ticker: str, analysis_results: dict) -> pd.DataFrame:
        """Create comparison DataFrame"""
        peers = self.get_sector_peers(ticker)
        
        # Create comparison data
        comparison_data = []
        
        # Add main ticker
        comparison_data.append({
            'Ticker': ticker,
            'Sector': self.SECTOR_MAP.get(ticker, 'Unknown'),
            'FinalScore': analysis_results.get('FinalScore', 0),
            'PER': analysis_results.get('PER', 0),
            'PBV': analysis_results.get('PBV', 0),
            'ROE': analysis_results.get('ROE', 0),
            'RSI': analysis_results.get('RSI', 50),
            'DividendYield': analysis_results.get('DividendYield', 0) or 0,
            'Label': analysis_results.get('Label', 'N/A')
        })
        
        # Add placeholder for peers (in real implementation, would analyze peers too)
        for peer in peers:
            comparison_data.append({
                'Ticker': peer,
                'Sector': self.SECTOR_MAP.get(peer, 'Unknown'),
                'FinalScore': np.random.randint(3, 8),  # Placeholder
                'PER': round(np.random.uniform(8, 25), 1),
                'PBV': round(np.random.uniform(1, 4), 2),
                'ROE': round(np.random.uniform(0.05, 0.25), 3),
                'RSI': round(np.random.uniform(30, 70), 1),
                'DividendYield': round(np.random.uniform(0.01, 0.05), 3),
                'Label': np.random.choice(['BUY', 'HOLD', 'AVOID'])
            })
        
        return pd.DataFrame(comparison_data)
    
    def create_radar_chart(self, comparison_df: pd.DataFrame):
        """Create radar chart comparison"""
        if len(comparison_df) < 2:
            return None
        
        # Normalize metrics for radar chart
        metrics = ['FinalScore', 'PER', 'PBV', 'ROE', 'RSI', 'DividendYield']
        
        fig = go.Figure()
        
        for _, row in comparison_df.iterrows():
            values = []
            for metric in metrics:
                if metric == 'PER':
                    # Lower PER is better (inverse)
                    val = 1 / (row[metric] + 0.1)  # Add small value to avoid division by zero
                elif metric == 'PBV':
                    # Lower PBV is better (inverse)
                    val = 1 / (row[metric] + 0.1)
                elif metric == 'RSI':
                    # RSI around 50 is best (bell curve)
                    val = 1 - abs(row[metric] - 50) / 50
                else:
                    # Higher is better (normalize to 0-1)
                    max_val = comparison_df[metric].max()
                    min_val = comparison_df[metric].min()
                    if max_val != min_val:
                        val = (row[metric] - min_val) / (max_val - min_val)
                    else:
                        val = 0.5
            
                values.append(max(0, min(1, val)))  # Clamp to 0-1
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics,
                fill='toself',
                name=row['Ticker']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Peer Comparison Radar Chart",
            height=500
        )
        
        return fig
    
    def create_comparison_table(self, comparison_df: pd.DataFrame):
        """Create styled comparison table"""
        # Highlight the main ticker
        def highlight_main(row):
            if row.name == 0:  # First row is main ticker
                return ['background-color: #e6f3ff'] * len(row)
            return [''] * len(row)
        
        styled_df = comparison_df.style.apply(highlight_main, axis=1)
        
        # Format percentages
        if 'ROE' in comparison_df.columns:
            styled_df = styled_df.format({'ROE': '{:.1%}'})
        
        if 'DividendYield' in comparison_df.columns:
            styled_df = styled_df.format({'DividendYield': '{:.2%}'})
        
        return styled_df
    
    def get_comparison_insights(self, comparison_df: pd.DataFrame) -> str:
        """Generate insights from comparison"""
        if len(comparison_df) < 2:
            return "Tidak ada data peer untuk perbandingan."
        
        main_ticker = comparison_df.iloc[0]
        peers_df = comparison_df.iloc[1:]
        
        insights = []
        
        # PER comparison
        avg_per = peers_df['PER'].mean()
        if main_ticker['PER'] < avg_per * 0.9:
            insights.append(f"✅ PER {main_ticker['Ticker']} ({main_ticker['PER']:.1f}x) lebih murah dari rata-rata sektor ({avg_per:.1f}x)")
        elif main_ticker['PER'] > avg_per * 1.1:
            insights.append(f"⚠️ PER {main_ticker['Ticker']} ({main_ticker['PER']:.1f}x) lebih mahal dari rata-rata sektor ({avg_per:.1f}x)")
        
        # ROE comparison
        avg_roe = peers_df['ROE'].mean()
        if main_ticker['ROE'] > avg_roe * 1.1:
            insights.append(f"✅ ROE {main_ticker['Ticker']} ({main_ticker['ROE']:.1%}) lebih tinggi dari rata-rata sektor ({avg_roe:.1%})")
        elif main_ticker['ROE'] < avg_roe * 0.9:
            insights.append(f"⚠️ ROE {main_ticker['Ticker']} ({main_ticker['ROE']:.1%}) lebih rendah dari rata-rata sektor ({avg_roe:.1%})")
        
        # Score ranking
        rank = (peers_df['FinalScore'] > main_ticker['FinalScore']).sum() + 1
        total = len(comparison_df)
        insights.append(f"📊 Peringkat {main_ticker['Ticker']}: {rank}/{total} berdasarkan skor analisis")
        
        return "\n\n".join(insights)
