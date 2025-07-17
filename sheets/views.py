from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
import pandas as pd
import numpy as np
import io
import json
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def upload_excel(request):
    df_data = None
    df_columns = None
    df_columns_json = '[]'
    table_mode = False
    form = ExcelUploadForm()
    totals = {}
    averages = {}

    summary_mode = 'both' 
    edit_mode = False      

    if request.method == 'POST':
        #summary_mode = request.POST.get('summary_mode', 'both')

        if 'upload' in request.POST:
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['file']
                df = pd.read_excel(excel_file)
                request.session['excel_data'] = df.to_json()
                table_mode = True
                edit_mode = False 

        elif 'edit' in request.POST:
            edit_mode = True
            table_mode = True

        elif 'save' in request.POST:
            rows = int(request.POST.get('rows'))
            cols = json.loads(request.POST.get('cols'))
            edited_data = []
            edit_mode = False

            for i in range(rows):
                row_data = {}
                for col in cols:
                    row_data[col] = request.POST.get(f'{col}_{i}')
                edited_data.append(row_data)

            df = pd.DataFrame(edited_data)
            request.session['excel_data'] = df.to_json()
            table_mode = True
            edit_mode = False  

        elif 'cancel' in request.POST:
            return redirect('upload_excel')

    excel_json = request.session.get('excel_data')
    if excel_json:
        df = pd.read_json(excel_json)
        df_columns = df.columns.tolist()
        df_columns_json = json.dumps(df_columns)
        df_data = df.values.tolist()
        table_mode = True

        numeric_cols = df.select_dtypes(include=np.number).columns
        totals = df[numeric_cols].sum().to_dict()
        averages = df[numeric_cols].mean().to_dict()

    context = {
        'form': form,
        'df_data': df_data,
        'df_columns': df_columns,
        'df_columns_json': df_columns_json,
        'table_mode': table_mode,
        'totals': totals,
        'averages': averages,
        'summary_mode': summary_mode,
        'edit_mode': edit_mode,
    }
    return render(request, 'sheets/dashboard.html', context)

@login_required
def export_excel(request):
    excel_json = request.session.get('excel_data')
    if not excel_json:
        return HttpResponse("No data to export", status=400)

    df = pd.read_json(excel_json)
    
    # Total nab Average
    numeric_cols = df.select_dtypes(include=np.number).columns
    totals = df[numeric_cols].sum()
    averages = df[numeric_cols].mean()
    
    # Summary role
    total_row = pd.DataFrame({col: [totals[col]] if col in totals else [''] for col in df.columns})
    average_row = pd.DataFrame({col: [averages[col]] if col in averages else [''] for col in df.columns})

    # Label
    if len(df.columns) > 0:
        total_row.iloc[0, 0] = 'Total'
        average_row.iloc[0, 0] = 'Average'

    # Append
    df_export = pd.concat([df, total_row, average_row], ignore_index=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=exported_data_with_summary.xlsx'
    return response




def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})