from django.core import serializers
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import re
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.platypus import Image as ReportImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import re
import csv
import io
import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import numpy as np
import pandas as pd
import scipy.io as sio
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy import signal as sig
import pandas as pd
import io
from PIL import Image
import re
import os
import datetime
from reportlab.platypus import (
    SimpleDocTemplate, PageTemplate, Frame, Paragraph, Spacer, ListFlowable,
    ListItem, Table, TableStyle, Image as ReportImage, PageBreak
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import google.generativeai as genai
import matplotlib.pyplot as plt
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import os
from django.conf import settings
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportImage
import re
import base64

from ml.Interface import Interface
from .models import MachineRecord,MonitorRecord


import warnings
warnings.filterwarnings("ignore")

# Create your views here.


def home(request):
    return render(request, "web/home.html")


def monitoring(request):
    return render(request, "web/bearings_prediction.html")


def explore(request):
    return render(request, "web/explore.html")


def plots(request):
    return render(request, "web/graph.html")


def delete_record(request, id):
    if request.method == "DELETE":
        record = MachineRecord.objects.filter(id=id)
        if record:
            record[0].delete()
            return HttpResponse("true")
        return HttpResponse("false")

def condition(request,id):
    record=MonitorRecord.objects.filter(id=id,user=request.user)
    if record:
        record=serializers.serialize('json',record)
        return render(request,"web/condition.html",{"record":record})
    return redirect("Home")


def dashboard(request, id):
    record = MachineRecord.objects.filter(id=id, user=request.user)
    if record:
        record = serializers.serialize('json', record)
        return render(request, "web/dashboard.html", {"record": record})
    return redirect("Home")


def process_file(file, power):
    data_set = file.read().decode("latin-1")
    df = pd.read_csv(io.StringIO(data_set))

    # Keeping only first column
    if (df.shape[1] > 1):
        cols = df.columns
        df = df[cols[0]]

    if (not df.shape[0] > 4000):
        return -1

    win_l = 4000
    stride = 800
    X = []
    for j in np.arange(0, len(df)-(win_l), stride):
        win = df.iloc[j:j+win_l, :].values
        win = win.reshape((1, -1))
        X.append(win)

    # Considering 10% from start and end
    last_rec = int((len(X)*0.1))
    X = X[:last_rec]+X[-last_rec:]
    for i in range(0, len(X)):
        X[i] = np.column_stack((X[i], power))
    return X



@login_required
def diagnose(request):
    if request.method == "POST" and request.FILES["vib_file"]:
        file = request.FILES["vib_file"]
        if not file.name.endswith(".csv"):
            return HttpResponse("Please use csv format only ")
        res = process_file(file, request.POST['power'])
        
        if res == -1:
            return HttpResponse("CSV File should contain atleast 5000 values")
        else:        
            name=request.POST["machine_name"]
            interface = Interface()
            result=interface.diagnose(res)
            print("In view:",result)
            rec=MonitorRecord(
                machine_name=name,user=request.user,predictions=result
                )
            rec.save()
            return redirect("Condition",id=rec.id)
        
@login_required()
def predict(request):
    if request.method == "POST":
        # Input
        model = request.POST["model"]
        air_temp = request.POST["air_temp"]
        process_temp = request.POST["process_temp"]
        rotational_speed = request.POST["rotational_speed"]
        torque = request.POST["torque"]
        tool_wear = request.POST["tool_wear"]
        name = request.POST["machine_name"]

        type = request.POST["type"]
        quality = -1
        if type == "low":
            quality = 0
        elif type == "high":
            quality = 2
        else:
            quality = 1

        # Auth

        list = [[air_temp, process_temp,
                 rotational_speed, torque,
                 tool_wear, quality]]

        preds = Interface.predict(list, model)
        record = MachineRecord(machine_name=name, user=request.user, air_temp=air_temp,
                               process_temp=process_temp, rotational_speed=rotational_speed,
                               torque=torque, tool_wear=tool_wear,
                               quality=quality, predictions=preds.tolist())
        record.save()
        return redirect("Dashboard", id=record.id)

    return render(request, "web/predict.html")

# Auth part


def login_user(request):
    if request.method == "POST":
        username = request.POST["loginusername"]
        password = request.POST["loginpass"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("Home")
        else:
            return redirect("Login")

    else:
        print(request.GET)
        return render(request, "web/login.html")


@login_required()
def history(request):
    data = MachineRecord.objects.filter(user=request.user)
    return render(request, "web/history.html", {'records': data})


def logout_user(request):
    logout(request)
    return redirect("Home")


def gen_name(name):
    name = name.split(" ")
    if len(name) == 2:
        return name[0], name[1]
    elif len(name) == 3:
        return name[0], name[2]
    else:
        return name[0], ""


def signup_user(request):
    if request.method == "POST":
        name = request.POST["fullname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        name = str(name).strip()

        f_name, l_name = gen_name(name)

        if not pass1 == pass2:
            return redirect("Signup")

        user = User.objects.create_user(username=email,
                                        first_name=f_name,
                                        last_name=l_name,
                                        password=pass1)
        if user:
            user.save()
            print("User created succesfully!")
            return redirect("Home")
        else:
            print("User already exists ")
            return redirect("Signup")

    else:
        return render(request, "web/signup.html")

# Function to convert markdown to plain text


def markdown_to_plain_text(markdown_text):
    # Remove headers (# Header)
    text = re.sub(r'#+\s+(.*)', r'\1', markdown_text)
    # Remove bold and italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\_\_(.*?)\_\_', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'\_(.*?)\_', r'\1', text)
    # Remove bullet points
    text = re.sub(r'^\s*[\*\-]\s+(.*)', r'\1', text, flags=re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+(.*)', r'\1', text, flags=re.MULTILINE)
    # Remove code blocks
    text = re.sub(r'```(?:\w+)?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Replace horizontal rules
    text = re.sub(r'^\s*[\*\-\_]{3,}\s*$', '\n\n', text, flags=re.MULTILINE)
    # Remove links but keep text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    return text

# Analyze vibration data function


def analyze_vibration_data(mat_file_path):
    # Load the MATLAB file
    mat_data = sio.loadmat(mat_file_path)

    # Inspect the keys to find the vibration data
    data_keys = [key for key in mat_data.keys() if not key.startswith('__')]

    # Assume the first available key holds the vibration signal
    signal_key = data_keys[0]
    vibration_signal = mat_data[signal_key].squeeze()

    # Define the sampling rate (51,200 samples per second as specified)
    sample_rate = 51200

    # Create a time axis in seconds
    time = np.arange(len(vibration_signal)) / sample_rate

    # Calculate signal statistics
    mean_val = np.mean(vibration_signal)
    std_val = np.std(vibration_signal)
    rms_val = np.sqrt(np.mean(np.square(vibration_signal)))
    crest_factor = np.max(np.abs(vibration_signal)) / rms_val
    kurtosis_val = np.sum((vibration_signal - mean_val)**4) / \
        (len(vibration_signal) * std_val**4)

    # Create signal stats dataframe for visualization
    stats_df = pd.DataFrame({
        'Metric': ['Mean', 'Standard Deviation', 'RMS', 'Crest Factor', 'Kurtosis'],
        'Value': [mean_val, std_val, rms_val, crest_factor, kurtosis_val]
    })

    # Calculate FFT for frequency domain analysis
    n = len(vibration_signal)
    fft_result = np.fft.rfft(vibration_signal * np.hanning(n))
    fft_magnitude = np.abs(fft_result) / n * 2
    freq = np.fft.rfftfreq(n, d=1/sample_rate)

    # Calculate spectrogram
    f, t, Sxx = sig.spectrogram(
        vibration_signal, fs=sample_rate, nperseg=1024, noverlap=512)

    # Create subplots for comprehensive visualization
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Time Domain Vibration Signal',
            'Frequency Spectrum (FFT)',
            'Spectrogram',
            'Statistical Metrics',
            'Signal Histogram',
            'Cepstrum Analysis'
        ),
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "bar"}],
            [{"type": "xy"}, {"type": "xy"}]
        ],
        vertical_spacing=0.13,
        horizontal_spacing=0.08
    )

    # 1. Time Domain Plot (with envelope)
    analytic_signal = sig.hilbert(vibration_signal)
    amplitude_envelope = np.abs(analytic_signal)

    fig.add_trace(
        go.Scatter(
            x=time,
            y=vibration_signal,
            mode='lines',
            line=dict(color='blue', width=1),
            name='Vibration Signal'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=time,
            y=amplitude_envelope,
            mode='lines',
            line=dict(color='red', width=1.5),
            name='Signal Envelope'
        ),
        row=1, col=1
    )

    # 2. Frequency Domain Plot (FFT)
    # Find dominant frequencies
    peak_indices = sig.find_peaks(
        fft_magnitude, height=np.max(fft_magnitude)/10)[0]
    peak_freqs = freq[peak_indices]
    peak_mags = fft_magnitude[peak_indices]

    fig.add_trace(
        go.Scatter(
            x=freq,
            y=fft_magnitude,
            mode='lines',
            line=dict(color='green', width=1.5),
            name='FFT Magnitude'
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=peak_freqs,
            y=peak_mags,
            mode='markers',
            marker=dict(size=8, color='red', symbol='circle'),
            name='Peak Frequencies',
            text=[f"{f:.1f} Hz" for f in peak_freqs],
            hoverinfo='text+y'
        ),
        row=1, col=2
    )

    # 3. Spectrogram
    fig.add_trace(
        go.Heatmap(
            x=t,
            y=f,
            z=10 * np.log10(Sxx),
            colorscale='Jet',
            name='Spectrogram',
            colorbar=dict(title="Power/dB")
        ),
        row=2, col=1
    )

    # 4. Statistical metrics
    fig.add_trace(
        go.Bar(
            x=stats_df['Metric'],
            y=stats_df['Value'],
            marker_color=['rgba(58, 71, 180, 0.6)', 'rgba(58, 71, 180, 0.6)',
                          'rgba(58, 71, 180, 0.6)', 'rgba(246, 78, 139, 0.6)',
                          'rgba(246, 78, 139, 0.6)'],
            text=[f"{val:.4f}" for val in stats_df['Value']],
            textposition='auto'
        ),
        row=2, col=2
    )

    # 5. Histogram of Signal Values
    fig.add_trace(
        go.Histogram(
            x=vibration_signal,
            nbinsx=50,
            marker_color='rgba(0, 128, 128, 0.7)',
            name='Amplitude Distribution'
        ),
        row=3, col=1
    )

    # Add normal distribution curve for comparison
    x_range = np.linspace(min(vibration_signal), max(vibration_signal), 100)
    y_normal = 1/(std_val * np.sqrt(2 * np.pi)) * \
        np.exp(-(x_range - mean_val)**2 / (2 * std_val**2))
    # Scale to match histogram height
    scaling_factor = len(vibration_signal) / 50 * \
        (max(vibration_signal) - min(vibration_signal))
    y_normal = y_normal * scaling_factor

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_normal,
            mode='lines',
            line=dict(color='red', width=2),
            name='Normal Distribution'
        ),
        row=3, col=1
    )

    # 6. Cepstrum Analysis
    cepstrum = np.real(np.fft.ifft(np.log(np.abs(fft_result) + 1e-10)))
    quefrency = np.arange(len(cepstrum)) / sample_rate

    fig.add_trace(
        go.Scatter(
            x=quefrency[:len(quefrency)//2],
            y=cepstrum[:len(cepstrum)//2],
            mode='lines',
            line=dict(color='purple', width=1.5),
            name='Cepstrum'
        ),
        row=3, col=2
    )

    # Update layout for better visualization
    fig.update_layout(
        title='Comprehensive Vibration Signal Analysis',
        height=1000,
        width=1200,
        template='plotly_white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(title_text="Time (seconds)", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", row=1, col=1)

    fig.update_xaxes(title_text="Frequency (Hz)", row=1, col=2)
    fig.update_yaxes(title_text="Magnitude", row=1, col=2)

    fig.update_xaxes(title_text="Time (seconds)", row=2, col=1)
    fig.update_yaxes(title_text="Frequency (Hz)", row=2, col=1)

    fig.update_xaxes(title_text="Metric", row=2, col=2)
    fig.update_yaxes(title_text="Value", row=2, col=2)

    fig.update_xaxes(title_text="Amplitude", row=3, col=1)
    fig.update_yaxes(title_text="Count", row=3, col=1)

    fig.update_xaxes(title_text="Quefrency (seconds)", row=3, col=2)
    fig.update_yaxes(title_text="Amplitude", row=3, col=2)

    return fig, stats_df

# Extract individual plots


def save_plot_to_image(fig, row, col, title):
    # Create a figure with just the specified subplot
    subplot_fig = make_subplots(rows=1, cols=1, subplot_titles=[title])

    # Get the traces from the main figure for the specified subplot
    traces = [trace for trace in fig.data if trace.xaxis == f'x{row*2-2+col}' or
              (row == 1 and col == 1 and trace.xaxis == 'x')]

    # Add the traces to the subplot figure
    for trace in traces:
        subplot_fig.add_trace(trace)

    # Update the layout
    subplot_fig.update_layout(
        height=500,
        width=600,
        template='plotly_white',
        showlegend=True
    )

    # Save to BytesIO object as PNG
    img_bytes = io.BytesIO()
    subplot_fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)

    return img_bytes

# Function to send image to Gemini API and get insights


def get_gemini_insights(image_bytes, plot_type, api_key):
    """Send an image to Gemini API and get insights"""
    # Configure the API
    genai.configure(api_key=api_key)

    # Open the image with PIL
    image = Image.open(image_bytes)

    # Create a model instance
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare the prompt based on plot type
    prompt_map = {
        "time_domain": "Analyze this time domain vibration signal plot. Identify any anomalies, patterns, or issues. Provide maintenance recommendations.",
        "frequency_spectrum": "Analyze this frequency spectrum (FFT) plot. Identify significant frequency components, harmonics, and potential fault frequencies. What machine conditions might these indicate?",
        "spectrogram": "Analyze this vibration spectrogram. Identify any time-varying frequency components, intermittent issues, or patterns that suggest machine faults.",
        "statistical_metrics": "Analyze these vibration statistical metrics. What do they indicate about the machine's condition? Are any metrics outside normal ranges?",
        "histogram": "Analyze this signal histogram. Is the distribution normal? What does the shape indicate about the vibration characteristics?",
        "cepstrum": "Analyze this cepstrum plot. Identify any periodic structures in the signal that might indicate bearing faults, gear mesh, or harmonics."
    }

    prompt = prompt_map.get(
        plot_type, "Analyze this vibration analysis plot. Provide insights and maintenance recommendations.")

    # Generate content
    response = model.generate_content([prompt, image])

    return response.text

# Analyze all plots with Gemini


def analyze_all_plots_with_gemini(fig, api_key):
    """Extract all subplots, send to Gemini API, and consolidate insights"""
    # Plot types and their positions
    plots = {
        "time_domain": (1, 1, "Time Domain Vibration Signal"),
        "frequency_spectrum": (1, 2, "Frequency Spectrum (FFT)"),
        "spectrogram": (2, 1, "Spectrogram"),
        "statistical_metrics": (2, 2, "Statistical Metrics"),
        "histogram": (3, 1, "Signal Histogram"),
        "cepstrum": (3, 2, "Cepstrum Analysis")
    }

    # Dictionary to store insights
    insights = {}
    plot_images = []  # Change to a list to store file paths

    # Process each plot
    for plot_type, (row, col, title) in plots.items():
        # Extract the subplot as an image
        img_bytes = save_plot_to_image(fig, row, col, title)

        # Save the image bytes to a temporary file
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_img.write(img_bytes.getvalue())
        temp_img.close()

        # Store the file path instead of the bytes
        plot_images.append({
            'type': plot_type,
            'path': temp_img.name,
            'title': title
        })

        # Get insights from Gemini
        try:
            img_bytes.seek(0)  # Reset position
            plot_insights = get_gemini_insights(img_bytes, plot_type, api_key)
            insights[plot_type] = plot_insights
        except Exception as e:
            insights[plot_type] = f"Error: {str(e)}"

    return insights, plot_images

# Generate consolidated report


def generate_consolidated_report(insights, stats_df, api_key):
    """Generate a consolidated report from all insights and statistical data"""
    # Configure the API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare the context with statistical data and insights
    context = f"""
    Vibration Analysis Statistical Data:
    - Mean: {stats_df.loc[0, 'Value']:.6f}
    - Standard Deviation: {stats_df.loc[1, 'Value']:.6f}
    - RMS: {stats_df.loc[2, 'Value']:.6f}
    - Crest Factor: {stats_df.loc[3, 'Value']:.6f}
    - Kurtosis: {stats_df.loc[4, 'Value']:.6f}

    Individual Plot Insights:

    1. Time Domain Analysis:
    {insights.get('time_domain', 'No insights available')}

    2. Frequency Spectrum Analysis:
    {insights.get('frequency_spectrum', 'No insights available')}

    3. Spectrogram Analysis:
    {insights.get('spectrogram', 'No insights available')}

    4. Statistical Metrics Analysis:
    {insights.get('statistical_metrics', 'No insights available')}

    5. Histogram Analysis:
    {insights.get('histogram', 'No insights available')}

    6. Cepstrum Analysis:
    {insights.get('cepstrum', 'No insights available')}
    """

    prompt = f"""
    Based on the vibration analysis data and insights provided, create a comprehensive report with the following sections:

    1. Executive Summary: Provide a brief overview of the machine's condition.
    2. Key Findings: List the most significant issues identified in the analysis.
    3. Detailed Analysis: Discuss what each plot reveals about the machine's condition.
    4. Maintenance Recommendations: Prioritized list of actions that should be taken.
    5. Severity Assessment: Rate the overall condition (Normal, Warning, Alarm, or Critical).

    Context:
    {context}
    """

    response = model.generate_content(prompt)
    return response.text

# Create PDF report


class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.pagesize = letter

    def beforePage(self):
        canvas = self.canv
        canvas.saveState()
        # Header: Report title at top-left
        canvas.setFont("Helvetica", 9)
        canvas.drawString(72, letter[1] - 36, "Vibration Analysis Report")
        # Footer: Page number at bottom-left
        page_number_text = "Page %d" % canvas.getPageNumber()
        canvas.drawString(72, 30, page_number_text)
        canvas.restoreState()

# Enhanced Markdown Parser: converts markdown text to ReportLab flowables.


def markdown_to_flowables(text, styles):
    """
    Converts markdown text to a list of ReportLab flowables.
    - Converts **bold text** to <b>text</b>
    - Converts *italic text* to <i>text</i>
    - Processes headings (#, ##, ###), bullet lists, and numbered lists.
      For numbered lists, sequential numbers are generated.
    """
    flowables = []
    lines = text.splitlines()
    list_buffer = []  # Buffer to accumulate list items
    current_list_type = None  # 'bullet' or 'numbered'

    def flush_list():
        nonlocal list_buffer, current_list_type, flowables
        if list_buffer:
            if current_list_type == 'bullet':
                lf = ListFlowable(
                    [ListItem(Paragraph(item, styles['Normal']))
                     for item in list_buffer],
                    bulletType='bullet'
                )
                flowables.append(lf)
            elif current_list_type == 'numbered':
                # Manually number the list items
                for i, item in enumerate(list_buffer, start=1):
                    numbered_paragraph = Paragraph(
                        f"{i}. {item}", styles['Normal'])
                    flowables.append(numbered_paragraph)
            flowables.append(Spacer(1, 6))
            list_buffer.clear()
            current_list_type = None

    for line in lines:
        line = line.strip()
        # Convert markdown bold **text** to ReportLab <b> tag
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        # Convert italics *text* to <i> tag (if needed)
        line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
        # Remove any extraneous leading bullet markers if needed
        if line.startswith("*"):
            line = line.lstrip("*").strip()
        if not line:
            flush_list()
            flowables.append(Spacer(1, 6))
            continue

        # Process headings based on markdown markers
        if line.startswith("### "):
            flush_list()
            flowables.append(Paragraph(line[4:], styles['Heading3']))
        elif line.startswith("## "):
            flush_list()
            flowables.append(Paragraph(line[3:], styles['Heading2']))
        elif line.startswith("# "):
            flush_list()
            flowables.append(Paragraph(line[2:], styles['Heading1']))
        # Bullet list items (starting with "- ")
        elif line.startswith("- "):
            if current_list_type and current_list_type != 'bullet':
                flush_list()
            current_list_type = 'bullet'
            list_buffer.append(line[2:])
        # Numbered list items (e.g. "1. ", "2. ", etc.)
        elif re.match(r'^\d+\.\s+', line):
            if current_list_type and current_list_type != 'numbered':
                flush_list()
            current_list_type = 'numbered'
            # Remove the original number and whitespace; numbering will be auto-generated.
            item_text = re.sub(r'^\d+\.\s+', '', line)
            list_buffer.append(item_text)
        else:
            flush_list()
            flowables.append(Paragraph(line, styles['Normal']))
        flowables.append(Spacer(1, 6))
    flush_list()
    return flowables

# Function to build the cover page and table of contents (combined on one page)


def build_cover_and_toc(metadata, styles):
    story = []
    # --- Cover Page ---
    cover_title = Paragraph("Vibration Analysis Report", styles['Title'])
    report_date = metadata.get(
        'report_date', datetime.date.today().strftime('%B %d, %Y'))
    cover_info = Paragraph(
        f"Date: {report_date}<br/>"
        f"Machine: {metadata.get('machine_name', 'Unknown Machine')}<br/>"
        f"Sensor Location: {metadata.get('sensor_location', 'Unknown Location')}",
        styles['Normal']
    )
    story.append(cover_title)
    story.append(Spacer(1, 12))
    story.append(cover_info)
    story.append(Spacer(1, 24))

    # --- Table of Contents ---
    toc_title = Paragraph("Table of Contents", styles['Heading1'])
    story.append(toc_title)
    toc_entries = [
        "1. Executive Summary",
        "2. Key Findings",
        "3. Detailed Analysis",
        "4. Maintenance Recommendations",
        "5. Severity Assessment",
        "6. Analysis Plots"
    ]
    for entry in toc_entries:
        story.append(Paragraph(entry, styles['Normal']))
        story.append(Spacer(1, 6))

    # End the combined cover and TOC page with a single page break
    story.append(PageBreak())
    return story

# Main function to create the PDF report


def create_pdf_report(report_text, plot_images, output_file, metadata):
    """
    Generates a comprehensive PDF report.
    
    Parameters:
      - report_text: Markdown-formatted report text.
      - plot_images: List of dicts with keys: 'type', 'path', 'title'
      - output_file: The output PDF file path.
      - metadata: Dictionary with keys like 'machine_name', 'sensor_location', 'report_date'
    """
    doc = MyDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Build combined cover page and table of contents (on one page)
    story.extend(build_cover_and_toc(metadata, styles))

    # --- Main Report Content ---
    content_flowables = markdown_to_flowables(report_text, styles)
    story.extend(content_flowables)
    story.append(PageBreak())

    # --- Analysis Plots Section ---
    story.append(Paragraph("Analysis Plots", styles['Heading1']))
    story.append(Spacer(1, 12))

    # Process images: create list items (each item is a list of flowables: title + image)
    image_items = []
    for plot_info in plot_images:
        img_path = plot_info['path']
        plot_title = plot_info.get(
            'title', plot_info['type'].replace("_", " ").title())
        if not os.path.exists(img_path):
            item = Paragraph(
                f"Error: Image for {plot_title} not found", styles['Normal'])
        else:
            title_paragraph = Paragraph(plot_title, styles['Heading3'])
            try:
                # Scale image to half the available width (minus padding) and fixed height
                img_flowable = ReportImage(
                    img_path, width=(doc.width / 2) - 12, height=150)
            except Exception as e:
                img_flowable = Paragraph(
                    f"Error including image: {str(e)}", styles['Normal'])
            item = [title_paragraph, Spacer(1, 6), img_flowable]
        image_items.append(item)

    # Arrange images in a table (two columns per row)
    rows = []
    for i in range(0, len(image_items), 2):
        row = []
        row.append(image_items[i])
        if i + 1 < len(image_items):
            row.append(image_items[i + 1])
        else:
            row.append('')  # Empty cell if odd number of images
        rows.append(row)

    if rows:
        tbl = Table(rows, colWidths=[doc.width / 2.0, doc.width / 2.0])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.gray),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.gray),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)

    doc.build(story)
    return output_file


def vibration_reports(request):
    """View to show all past vibration analysis reports"""
    reports = VibrationAnalysisRecord.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, "web/vibration_reports.html", {'reports': reports})


def download_vibration_report(request, record_id):
    """View to re-download a previously generated report"""
    record = VibrationAnalysisRecord.objects.filter(
        id=record_id, user=request.user).first()
    if not record:
        return redirect('vibration_reports')

    # Create a PDF from the stored report text
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{record.machine_name}_vibration_report.pdf"'

    # Create a simple PDF with just the text (no images since they're not stored)
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50,
                 f"Vibration Analysis Report: {record.machine_name}")

    # Date
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80,
                 f"Generated: {record.created_at.strftime('%Y-%m-%d %H:%M')}")

    # Report content
    p.setFont("Helvetica", 10)
    text_object = p.beginText(50, height - 120)

    # Split the text into lines and add to PDF
    lines = record.report_text.split("\n")
    for line in lines:
        text_object.textLine(line)

    p.drawText(text_object)
    p.showPage()
    p.save()

    return response

# Django view for vibration analysis


def vibration_analysis(request):
    if request.method == "POST" and request.FILES.get("vibration_file"):
        file = request.FILES["vibration_file"]
        machine_name = request.POST.get("machine_name", "Unknown Machine")

        # Check if it's a MATLAB file
        if not file.name.endswith(".mat"):
            return HttpResponse("Please upload a MATLAB (.mat) file")

        # Save the uploaded file temporarily
        fs = FileSystemStorage(location=tempfile.gettempdir())
        filename = fs.save(file.name, file)
        file_path = os.path.join(fs.location, filename)

        # Initialize variables for cleanup
        html_path = None
        pdf_path = None
        temp_image_paths = []  # Track image files for cleanup

        try:
            # Get the Gemini API key from settings
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key:
                return HttpResponse("Gemini API key not configured")

            # Analyze vibration data
            fig, stats_df = analyze_vibration_data(file_path)

            # Save the figure to a temp HTML file for viewing
            html_path = os.path.join(
                fs.location, f"{os.path.splitext(filename)[0]}_analysis.html")
            fig.write_html(html_path)

            # Get AI insights and generate a report
            insights, plot_images = analyze_all_plots_with_gemini(fig, api_key)

            # Track image paths for cleanup
            for plot_info in plot_images:
                temp_image_paths.append(plot_info['path'])

            # Generate the report
            report_text = generate_consolidated_report(
                insights, stats_df, api_key)

            # Convert markdown to plain text
            plain_text_report = markdown_to_plain_text(report_text)

            # Create a PDF report
            pdf_path = os.path.join(
                fs.location, f"{os.path.splitext(filename)[0]}_report.pdf")

            metadata = {
                'machine_name': machine_name,  # or any value
                'sensor_location': 'Your Sensor Location',  # update accordingly
                'report_date': datetime.date.today().strftime('%B %d, %Y')  # or dynamic date, e.g., datetime.date.today().strftime('%B %d, %Y')
            }
            create_pdf_report(report_text, plot_images, pdf_path, metadata)

            # Save the report in the record model
            from .models import VibrationAnalysisRecord
            record = VibrationAnalysisRecord(
                machine_name=machine_name,
                user=request.user,
                report_text=plain_text_report,
                file_name=file.name
            )
            record.save()

            # Return the PDF as a download response
            with open(pdf_path, 'rb') as pdf:
                response = HttpResponse(
                    pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{machine_name}_vibration_report.pdf"'
                return response

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return HttpResponse(f"Error analyzing vibration data: {str(e)}<br><pre>{error_details}</pre>")

        finally:
            # Clean up temporary files
            all_temp_files = [file_path, html_path,
                              pdf_path] + temp_image_paths
            for path in all_temp_files:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"Failed to remove {path}: {str(e)}")

    # If GET or any other method, show the upload form
    return render(request, "web/vibration_analysis.html")
