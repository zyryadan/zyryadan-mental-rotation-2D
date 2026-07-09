import pandas as pd
import json
import re
import glob
import os

'''
Function to export data from .csv
Original .csv files are not the part of the project because of containing sensitive data 
Usage: python data.py
'''


def extract_useful_data():
    files = glob.glob("research_*.csv")

    if not files:
        print("CSV no data.")
        return

    summary_data = []

    for filepath in files:
        try:
            df = pd.read_csv(filepath)
            file_id = os.path.basename(filepath).replace(".csv", "")
            age = df.get('Participant_Age', pd.Series([None] * len(df))).iloc[-1]
            gender = df.get('Participant_Gender', df.get('Participant_Sex', pd.Series([None] * len(df)))).iloc[-1]
            strategy = df.get('Participant_Strategy', pd.Series([None] * len(df))).iloc[-1]
            sleep = df.get('Participant_Sleep', pd.Series([None] * len(df))).iloc[-1]
            energy = df.get('Participant_Energy', pd.Series([None] * len(df))).iloc[-1]
            if pd.isna(age) or pd.isna(gender) or pd.isna(strategy) or pd.isna(sleep) or pd.isna(energy):
                survey_rows = df[df['trial_type'] == 'survey-html-form']
                for _, row in survey_rows.iterrows():
                    try:
                        resp_json = json.loads(row['response'])

                        if pd.isna(age) and 'age' in resp_json:
                            age = resp_json['age']

                        if pd.isna(gender):
                            if 'gender' in resp_json:
                                gender = resp_json['gender']
                            elif 'sex' in resp_json:
                                gender = resp_json['sex']

                        if pd.isna(strategy) and 'strategy' in resp_json:
                            strategy = resp_json['strategy']

                        if pd.isna(sleep) and 'sleep' in resp_json:
                            sleep = resp_json['sleep']

                        if pd.isna(energy) and 'energy' in resp_json:
                            energy = resp_json['energy']

                    except:
                        continue

            questions_data = {}
            total_correct = 0
            total_rt = 0
            question_count = 0

            img_pattern = re.compile(r'(\d+)\.(?:jpeg|jpg|png)')

            for _, row in df.iterrows():
                stimulus = str(row.get('stimulus', ''))

                match = img_pattern.search(stimulus)
                if match:
                    q_num = int(match.group(1))

                    if 'correct' in row and not pd.isna(row['correct']):
                        is_correct = row['correct']
                        if isinstance(is_correct, str):
                            is_correct = is_correct.lower() == 'true'

                        rt = row['rt']

                        questions_data[f'Q{q_num}_Correct'] = 1 if is_correct else 0
                        questions_data[f'Q{q_num}_RT'] = rt

                        if is_correct:
                            total_correct += 1
                        total_rt += rt
                        question_count += 1

            if question_count == 0:
                accuracy = 0
                avg_rt = 0
            else:
                accuracy = round((total_correct / question_count) * 100, 2)
                avg_rt = round(total_rt / question_count, 2)

            participant_entry = {
                'File': file_id,
                'Age': age,
                'Gender': gender,
                'Sleep_Hours': sleep,
                'Energy_Level': energy,
                'Strategy': strategy,
                'Total_Accuracy_%': accuracy,
                'Avg_RT_ms': avg_rt,
                'Questions_Attempted': question_count
            }

            participant_entry.update(questions_data)
            summary_data.append(participant_entry)

        except Exception as e:
            print(f"Error {filepath}: {e}")

    if summary_data:
        result_df = pd.DataFrame(summary_data)

        main_cols = ['File', 'Age', 'Gender', 'Sleep_Hours', 'Energy_Level', 'Strategy', 'Total_Accuracy_%',
                     'Avg_RT_ms', 'Questions_Attempted']

        q_cols = sorted([c for c in result_df.columns if c not in main_cols],
                        key=lambda x: (int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0, x))

        final_cols = main_cols + q_cols
        final_cols = [c for c in final_cols if c in result_df.columns]

        result_df = result_df[final_cols]

        output_filename = 'summary_results.csv'
        result_df.to_csv(output_filename, index=False)
        print(f"\nDone: {output_filename}")
    else:
        print("Failure")


if __name__ == "__main__":
    extract_useful_data()
