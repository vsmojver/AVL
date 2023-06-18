import functions
import pandas as pd

# User inputed information
filenames = ["003_B1_SN2c2_FL_3500rpm_fl2.gid",
             "004_B1_SN1c7_FL_3750rpm_fl2.gid"]
channel = ":flow:total_mass"
output_folder = '/output_folder'

summary = pd.DataFrame()
for filename in filenames:
    speed, channel_name, unit, data = functions.preprocess_data(filename)
    data.columns = channel_name
    labels = dict(zip(channel_name, unit))
    if functions.detect_mass(channel):
        data[channel] = data[channel] * 1000
        labels[channel] = 'g'

    summary = pd.concat([summary, data[channel]], axis=1)
    functions.plot_gidas_files(speed, channel, data, labels, output_folder)

summary['Mean'] = summary.mean(axis=1)
report = pd.concat([data['CrankAngle'], summary['Mean']], axis=1)
report = report.rename(
    columns={'CrankAngle': f'CrankAngle  ({labels["CrankAngle"]})',
             'Mean': f'Average Value ({labels[channel]})'
             }
    )
with open(f"{output_folder}/report.txt", 'w') as f:
    report = report.to_string(index=False)
    f.write(report)

functions.plot_average_value(
    summary['Mean'], channel, data, labels, output_folder
)
