import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.graph_objects as go


class RiskAnalystEVT:
    def __init__(self, data):
        self.data = np.sort(data)

    def fit_gpd(self, threshold_quantile=0.95):
        """
        Peak-over-Threshold (POT) method using Generalized Pareto Distribution.
        """
        threshold = np.quantile(self.data, threshold_quantile)
        exceedances = self.data[self.data > threshold] - threshold

        # Fit GPD: shape (c), location (loc), scale (scale)
        shape, loc, scale = stats.genpareto.fit(exceedances)

        return {
            "threshold": threshold,
            "shape": shape,
            "scale": scale,
            "exceedances": exceedances
        }

    def plot_tail_risk(self):
        # Fit the model
        model = self.fit_gpd()
        threshold = model['threshold']

        # Generate distribution curve for the tail
        x = np.linspace(threshold, self.data.max() * 1.5, 100)
        y_gpd = stats.genpareto.pdf(x - threshold, model['shape'], 0, model['scale'])

        # Calculate Return Levels (e.g., 1-in-100 events)
        # Simplified for visualization
        return_level_100 = threshold + (model['scale'] / model['shape']) * ((100 * 0.05) ** model['shape'] - 1)

        # Plotting with Plotly
        fig = go.Figure()

        # 1. Histogram of historical data
        fig.add_trace(go.Histogram(x=self.data, nbinsx=50, name='Historical Data',
                                   marker_color='#34495e', opacity=0.75))

        # 2. Threshold Line
        fig.add_hline(y=0, line_width=1, line_color="black")
        fig.add_vline(x=threshold, line_dash="dash", line_color="#e67e22",
                      annotation_text="95% Threshold")

        # 3. 1-in-100 Year Event Marker
        fig.add_vline(x=return_level_100, line_width=3, line_color="#c0392b",
                      annotation_text="Black Swan (1-in-100)")

        fig.update_layout(
            title="Tail Risk Analysis: Identifying Black Swan Events",
            xaxis_title="Magnitude of Event (e.g., % Oil Price Drop)",
            yaxis_title="Frequency",
            template="plotly_white",
            showlegend=True
        )

        fig.write_html("risk_evt_analysis.html")
        print(f"Strategic Risk Analysis saved to: risk_evt_analysis.html")


# --- Example Execution ---
if __name__ == "__main__":
    # Generating mock oil price volatility (Log-normal with some extreme outliers)
    np.random.seed(42)
    normal_vol = np.random.normal(0, 2, 1000)
    black_swans = np.random.pareto(2, 50) * 10  # Extreme outliers
    oil_volatility = np.abs(np.concatenate([normal_vol, black_swans]))

    analyst = RiskAnalystEVT(oil_volatility)
    analyst.plot_tail_risk()