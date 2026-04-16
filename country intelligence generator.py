import wikipedia
import wbgapi as wb
import pandas as pd
import json
import os
from datetime import datetime


class IntelligenceDossier:
    def __init__(self, country_name, country_code):
        self.country_name = country_name
        self.country_code = country_code.upper()
        self.cache_file = f"cache_{self.country_code.lower()}.json"

    def fetch_wiki_summary(self):
        """Retrieves country profile from Wikipedia."""
        print(f"[*] Accessing Wikipedia for {self.country_name}...")
        wikipedia.set_lang("en")
        try:
            page = wikipedia.page(self.country_name)
            return {"summary": page.summary[:2000], "url": page.url}
        except Exception as e:
            return {"summary": "Profile summary unavailable.", "url": "N/A"}

    def fetch_world_bank_data(self):
        """Retrieves economic indicators with fallback to local cache."""
        print(f"[*] Accessing World Bank database for {self.country_code}...")
        indicators = {
            'GDP (Current US$)': 'NY.GDP.MKTP.CD',
            'Inflation (CPI %)': 'FP.CPI.TOTL.ZG',
            'Population (Total)': 'SP.POP.TOTL',
            'Ease of Doing Business': 'IC.BUS.EASE.XQ'  # Example indicator
        }

        try:
            # Fetching Most Recent Value (mrv=1)
            data = wb.data.dataframe(indicators.values(), self.country_code, mrv=1)
            results = {}
            for name, code in indicators.items():
                val = data.loc[code].values[0]
                results[name] = f"{val:,.2f}" if not pd.isna(val) else "N/A"

            # Save to cache if successful
            with open(self.cache_file, 'w') as f:
                json.dump(results, f)
            return results

        except Exception as e:
            print(f"[!] World Bank API Error. Checking local cache...")
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            return {"Status": "Offline", "Error": "Service unavailable and no cache found."}

    def generate_strategic_analysis(self, summary):
        """
        Structural Analysis (PEST framework).
        In production, replace with: openai.ChatCompletion.create(...)
        """
        return {
            "Political": "Stable parliamentary democracy with focus on Pacific regionalism.",
            "Economic": "Agro-export oriented; critical dependence on maritime logistics.",
            "Social": "Aging population with high demand for skilled digital migration.",
            "Technological": "Global leader in space-launch cost efficiency (Rocket Lab)."
        }

    def save_report(self):
        wiki = self.fetch_wiki_summary()
        economy = self.fetch_world_bank_data()
        pest = self.generate_strategic_analysis(wiki['summary'])

        filename = f"{self.country_name}_Strategic_Dossier.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Strategic Intelligence Dossier: {self.country_name}\n")
            f.write(f"**Status:** Confirmed | **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

            f.write("## I. Executive Summary\n")
            f.write(f"{wiki['summary']}\n\n")

            f.write("## II. Macroeconomic Indicators\n")
            f.write("| Indicator | Value |\n|---|---|\n")
            for k, v in economy.items():
                f.write(f"| {k} | {v} |\n")

            f.write("\n## III. PEST Analysis (AI Assisted)\n")
            for factor, desc in pest.items():
                f.write(f"- **{factor}:** {desc}\n")

            f.write(f"\n\n---\n*Sources: World Bank Open Data, Wikipedia Foundation. Compiled by IntelligenceGen.*")

        print(f"\n[DONE] Strategic report saved to: {filename}")


if __name__ == "__main__":
    # Example: New Zealand (NZL)
    dossier = IntelligenceDossier("New Zealand", "NZL")
    dossier.save_report()