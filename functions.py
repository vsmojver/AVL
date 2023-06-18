from typing import Tuple

import pandas as pd
import re
import matplotlib.pyplot as plt

CHANNEL_NAME_REGEX = r"CHANNELNAME=(\[.*?\])"
UNIT_REGEX = r"UNIT=(\[.*?\])"
END_OF_INPUT_LINE = "END"
TOTAL_MASS_REGEX = "total_mass"


def preprocess_data(filename: str) -> Tuple:
    """
    Preprocesses the data and ouputs:
    lists: channels, units
    DataFrame: Data
    string: speed
    """
    input_lines = _get_lines(filename)
    speed = _get_speed(filename)
    headers, data = map(str.strip, input_lines.split(END_OF_INPUT_LINE))
    headers = _prepare_headers_for_parsing(headers)

    # Channel
    channel_name_str = re.search(CHANNEL_NAME_REGEX, headers).group(1)
    channel_name = eval(channel_name_str)

    # Unit
    unit_str = re.search(UNIT_REGEX, headers).group(1)
    unit = eval(unit_str)

    # Data
    df = pd.DataFrame(data.split())
    data = pd.DataFrame(df.values.reshape(
        int(len(df)/len(channel_name)), len(channel_name))).astype('float')

    return speed, channel_name, unit, data


def _get_lines(filename: str) -> str:
    """
    Reads filename (a text file) and returns string
    """
    with open(filename, 'r') as f:
        return f.read()


def _get_speed(filename: str) -> str:
    """
    Helper function
    Gets speed in rpms from file name
    """

    match = re.search(r'\d+rpm', filename)
    if match:
        return match.group()


def _prepare_headers_for_parsing(headers: str) -> str:
    """
    Prepares headers from parsing by cleaning string
    """
    return headers.replace("&", "").replace("\n", "").replace(" ", '').replace("BEGIN", '')


def plot_gidas_files(speed, channel, data, labels, output_folder):
    """
    Plots selected channale versus crank angle
    Exports a file containing the diagram to output
    """
    cleaned_channel = _clean_channel_name(channel)
    plt.title(f'{cleaned_channel} @{speed}', fontsize=20)
    plt.xlabel('Crank Angle (deg)', fontsize=17)
    plt.ylabel(f'{cleaned_channel} ({labels[channel]})', fontsize=17)
    plt.plot(data['CrankAngle'], data[channel], color='red',
             label=f'{cleaned_channel} ({labels[channel]})')
    plt.grid(linestyle='--')
    plt.legend(loc="upper right")
    plt.savefig(f"{output_folder}/{cleaned_channel} {speed}.png")
    plt.show()


def plot_average_value(summary, channel, data, labels, output_folder):
    """
    Plots average value versus crank angle
    Exports a file containing the diagram to output
    """
    cleaned_channel = _clean_channel_name(channel)
    plt.title(f'Average {cleaned_channel}', fontsize=20)
    plt.xlabel('Crank Angle (deg)', fontsize=17)
    plt.ylabel(f'Average {cleaned_channel} ({labels[channel]})', fontsize=17)
    plt.plot(data['CrankAngle'], summary, color='blue',
             label=f'Average {cleaned_channel} ({labels[channel]})')
    plt.grid(linestyle='--')
    plt.legend(loc="upper right")
    plt.savefig(output_folder + '/Results for average value.png')
    plt.show()


def _clean_channel_name(channel: str) -> str:
    """
    Cleans channel name for use in graph label
    :flow:total_mass -> Total Mass
    """
    output = re.sub(':.*?:', '', channel)
    formatted_channel = output.replace('_', ' ').title()
    return formatted_channel


def detect_mass(text: str) -> bool:
    """
    Task specific function
    Detects if the selected channel is "Total Mass"
    """
    return bool(re.search(pattern=TOTAL_MASS_REGEX, string=text, flags=re.I))
