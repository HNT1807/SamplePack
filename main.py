import streamlit as st
import pandas as pd
import re

def process_file(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)

    if 18 in df.columns and 22 in df.columns:
        # Filter rows that contain 'Full' in the 19th column (index 18)
        df_full_tracks = df[df[18].astype(str).str.contains('Full', na=False)]
        composers = {}
        num_tracks = len(df_full_tracks)  # Count the number of tracks

        for _, row in df_full_tracks.iterrows():
            composer_data = str(row[22]).split(',')
            for composer_entry in composer_data:
                parts = composer_entry.split('(')
                if len(parts) > 1:
                    name = parts[0].strip()
                    pro_and_percent = parts[1].split(')')
                    if len(pro_and_percent) > 1:
                        pro = pro_and_percent[0].strip()
                        ipi_match = re.search(r'\[(.*?)\]', composer_entry)
                        ipi = ipi_match.group(1) if ipi_match else ""
                        percentage_match = re.search(r'\d+', pro_and_percent[1])
                        if percentage_match:
                            percentage = int(percentage_match.group())
                            points = percentage
                            composers[name] = {
                                'points': composers.get(name, {}).get('points', 0) + points,
                                'pro': pro,
                                'ipi': ipi
                            }

        total_points = sum(composer['points'] for composer in composers.values())
        max_possible_points = num_tracks * 100
        for composer in composers:
            composers[composer]['percentage'] = 100 * composers[composer]['points'] / max_possible_points if max_possible_points > 0 else 0

        return composers, num_tracks, max_possible_points
    else:
        return None, 0, 0


st.title('Composer Contribution Analyzer')

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
if uploaded_file is not None:
    composers, num_tracks, max_possible_points = process_file(uploaded_file)
    if composers:

        # Sorting composers by percentage in descending order
        sorted_composers = sorted(composers.items(), key=lambda x: x[1]['percentage'], reverse=True)

        formatted_composers = ", ".join(
            [f"{name} ({data['pro']}) {data['percentage']:.2f}% [{data['ipi']}]" for name, data in sorted_composers])
        st.write(f"{formatted_composers}")
        # Displaying the number of tracks and the maximum possible points
        st.write(f"The album has {num_tracks} tracks ({max_possible_points} points)")
        for composer, data in sorted_composers:
            st.write(f"{composer}: {data['points']} points ({data['percentage']:.2f}%)")


    else:
        st.write("Invalid file or file format")
