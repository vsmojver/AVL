import functions
import PySimpleGUI as sg
import pandas as pd

# channel = ':flow:total_mass'

label = sg.Text("Dashboard")
label_1 = sg.Text("Select files to analyse: ")
input_1 = sg.Input()
choose_button_1 = sg.FilesBrowse("Choose", key="input_files")

label_2 = sg.Text("Select folder to ouput analysis: ")
input_2 = sg.Input()
choose_button_2 = sg.FolderBrowse("Choose", key="output_folder")

label_3 = sg.Text("Input channel name")
input_3 = sg.InputText(default_text=':flow:total_mass', tooltip="Enter channel name", key="channel")

generate_report_button = sg.Button("Generate Report")

layout = [[label_1, input_1, choose_button_1],
          [label_2, input_2, choose_button_2],
          [label_3, input_3],
          [generate_report_button]
          ]

window = sg.Window("Report Generator", layout)


event, values = window.read()
filepaths = values["input_files"].split(";")
output_folder = values["output_folder"]
channel = values['channel']
summary = pd.DataFrame()
for filename in filepaths:
    speed, channel_name, unit, data = functions.preprocess_data(filename)
    data.columns = channel_name
    labels = dict(zip(channel_name, unit))
    if functions.detect_mass(channel):
        data[channel] = data[channel]*1000
        labels[channel] = 'g'

    summary = pd.concat([summary, data[channel]], axis=1)
    functions.plot_gidas_files(speed, channel, data, labels, output_folder)

summary['Mean'] = summary.mean(axis=1)
report = pd.concat([data['CrankAngle'], summary['Mean']], axis=1)
report = report.rename(columns={
    'CrankAngle': f'CrankAngle  ({labels["CrankAngle"]})', 'Mean': f'Average Value ({labels[channel]})'})

with open(f"{output_folder}/report.txt", 'w') as f:
    report = report.to_string(index=False)
    f.write(report)
functions.plot_average_value(
    summary['Mean'], channel, data, labels, output_folder)

window.close()
