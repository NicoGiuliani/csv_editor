from datetime import datetime
import json
import os
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponse
import pandas as pd
from dateutil import parser
from django.contrib.sessions.models import Session

from django.contrib import messages

import csv

# Create your views here.
# appname/views.py
last_uploaded_csv_data = None
initial = 0
headers = []
ascending = {}
most_recent_search_results = {}
filename = ""


def home(request):
    global last_uploaded_csv_data
    global initial
    global headers
    global most_recent_search_results
    global filename

    df = last_uploaded_csv_data
    context = {}

    most_recent_search_results = None

    if df is not None:
        json_string = df.to_json(orient="records")
        json_data = json.loads(json_string)

        context = {
            "display_headers": headers,
            "data": json_data,
            "initial": initial,
            "filename": filename,
            "searchFiltersActive": True
            if most_recent_search_results is not None
            else False,
        }

    return render(request, "index.html", context)


def test(request):
    return render(request, "test.html")


def export(request):
    global last_uploaded_csv_data
    global initial

    if last_uploaded_csv_data is None:
        return redirect("/")

    # Specify the file path where you want to save the CSV file
    csv_file_path = "output_file.csv"
    df = last_uploaded_csv_data

    # Columns to ignore
    columns_to_ignore = ["unique_index"]

    # Create a new DataFrame without the specified columns
    df_without_columns = df.drop(columns=columns_to_ignore)
    print("df:", df_without_columns)

    # Export the DataFrame to a CSV file
    # df.to_csv(csv_file_path, index=False)
    # json_string = df.to_json(orient="records")
    # json_data = json.loads(json_string)
    # print(type(json_data))
    # context = {"data": json_data}
    print(f"DataFrame has been exported to {csv_file_path}")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="export.csv"'
    df_without_columns.to_csv(
        path_or_buf=response, index=False
    )  # with other applicable parameters
    # Delete the CSV file
    # try:
    #     os.remove(csv_file_path)
    #     print(f"{csv_file_path} has been deleted.")
    # except FileNotFoundError:
    #     print(f"{csv_file_path} not found. It may not have been created.")
    # except Exception as e:
    #     print(f"An error occurred while deleting {csv_file_path}: {e}")

    return response


def delete(request, id):
    global last_uploaded_csv_data
    global initial
    global headers
    global most_recent_search_results
    global filename

    df = last_uploaded_csv_data
    print("here")

    # if most_recent_search_results is not None:
    #   print("now here")
    #   json_data = most_recent_search_results
    #   most_recent_dataframe = pd.DataFrame(most_recent_search_results)
    #   most_recent_df = most_recent_dataframe.drop(df[df["unique_index"] == int(id)].index)
    #   most_recent_df = most_recent_df.drop(df[df["unique_index"] == id].index)
    #   json_string = most_recent_df.to_json(orient="records")
    #   json_data = json.loads(json_string)

    print(df)
    print("Boom:", type(id))
    print("Bing:", id)
    df = df.drop(df[df["unique_index"] == int(id)].index)
    df = df.drop(df[df["unique_index"] == id].index)
    print("Deleted ID:", id)

    last_uploaded_csv_data = df

    # if most_recent_search_results is None:
    json_string = df.to_json(orient="records")
    json_data = json.loads(json_string)

    if most_recent_search_results is not None:
        print("filtered")
        df = pd.DataFrame(most_recent_search_results)
        df = df.drop(df[df["unique_index"] == int(id)].index)
        df = df.drop(df[df["unique_index"] == id].index)
        print(df)
        json_string = df.to_json(orient="records")
        json_data = json.loads(json_string)
        most_recent_search_results = json_data
        if len(json_data) == 0:
            return redirect("/")

    context = {
        "display_headers": headers,
        "data": json_data,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }
    return render(request, "index.html", context)


def edit(request, id):
    global last_uploaded_csv_data
    global initial
    global headers
    global filename
    global most_recent_search_results

    print("edit")
    df = last_uploaded_csv_data
    print(df)
    print("id:", id)

    # this is made a string for now, may have to change later
    to_edit = df.loc[df["unique_index"] == int(id)]
    print(to_edit)

    last_uploaded_csv_data = df
    json_string = df.to_json(orient="records")
    json_data = json.loads(json_string)

    to_edit_json_string = to_edit.to_json(orient="records")
    json_to_edit_data = json.loads(to_edit_json_string)
    print(json_to_edit_data)

    if most_recent_search_results is not None:
        json_data = most_recent_search_results

    context = {
        "display_headers": headers,
        "data": json_data,
        "to_edit": json_to_edit_data[0],
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }
    return render(request, "index.html", context)


def create(request):
    global last_uploaded_csv_data
    global initial
    global headers
    global filename
    global most_recent_search_results

    most_recent_search_results = None

    if request.method == "POST":
        post_data = request.POST
        new_data = {}

        for entry in post_data:
            if entry == "csrfmiddlewaretoken":
                continue
            new_data[entry] = post_data.get(entry)

        new_data["unique_index"] = int(new_data["unique_index"])
        print("new_data:", new_data)

        df = last_uploaded_csv_data
        # headers = df.columns.tolist()
        new_data_df = pd.DataFrame([new_data])
        df = pd.concat([df, new_data_df], ignore_index=True)
        last_uploaded_csv_data = df
        json_string = df.to_json(orient="records")
        json_data = json.loads(json_string)

        print("json_data:", json_data)
        initial += 1
        context = {
            "data": json_data,
            "display_headers": headers,
            "initial": initial,
            "filename": filename,
            "searchFiltersActive": True
            if most_recent_search_results is not None
            else False,
        }

    return render(request, "index.html", context)


def update(request):
    global last_uploaded_csv_data
    global initial
    global headers
    global filename
    global most_recent_search_results

    if request.method == "POST":
        post_data = request.POST
        new_data = {}

        for entry in post_data:
            if entry == "csrfmiddlewaretoken":
                continue
            new_data[entry] = post_data.get(entry)

        keys = list(new_data.keys())

        df = last_uploaded_csv_data
        i = new_data["unique_index"]
        underscored_headers = df.columns.tolist()
        json_string = df.to_json(orient="records")
        json_data = json.loads(json_string)

        df.loc[df["unique_index"] == int(i), underscored_headers] = list(
            map(lambda x: new_data[x], underscored_headers)
        )
        df.loc[df["unique_index"] == i, "unique_index"] = int(i)

        last_uploaded_csv_data = df
        json_string = df.to_json(orient="records")
        json_data = json.loads(json_string)

        if most_recent_search_results is not None:
            df = pd.DataFrame(most_recent_search_results)
            df.loc[df["unique_index"] == int(i), underscored_headers] = list(
                map(lambda x: new_data[x], underscored_headers)
            )
            df.loc[df["unique_index"] == i, "unique_index"] = int(i)
            json_string = df.to_json(orient="records")
            json_data = json.loads(json_string)
            most_recent_search_results = json_data

        context = {
            "data": json_data,
            "display_headers": headers,
            "initial": initial,
            "filename": filename,
            "searchFiltersActive": True
            if most_recent_search_results is not None
            else False,
        }

    # return redirect("home")
    return render(request, "index.html", context)


def upload(request):
    global last_uploaded_csv_data
    global initial
    global headers
    global filename
    global most_recent_search_results
    global filename

    most_recent_search_results = None

    if request.method == "POST":
        csv_file = request.FILES["csvFile"]
        filename = csv_file
        print("name:", csv_file)

        df = pd.read_csv(csv_file)
        # df.columns = df.columns.str.replace('/', '_')

        json_string = df.to_json(orient="records")
        json_data = json.loads(json_string)

        headers = df.columns.tolist()

        final_data = []
        initial = 0
        for entry in json_data:
            dictionary = {"unique_index": initial}
            initial += 1
            # data_headers = []
            for header in headers:
                # header_joined = "_".join(header.lower().split(' '))
                # data_headers.append(header_joined)
                # print("type:", type(header))
                # print("isvaliddate?:", is_valid_date(header))
                # date_format = "%m/%d/%Y"
                # temp = convert_to_valid_date(str(entry[header]), date_format)
                # if temp is not None:
                #    print("converted")
                #    entry[header] = temp
                #    dictionary[header] = entry[header]
                # else:
                ascending[header] = True
                dictionary[header] = str(entry[header])
            final_data.append(dictionary)

        headers.insert(0, "Unique Index")
        headers.insert(0, "Delete")
        headers.insert(0, "Edit")

        new_df = pd.DataFrame(final_data)
        last_uploaded_csv_data = new_df

        context = {
            "display_headers": headers,
            "data": final_data,
            "initial": initial,
            "filename": filename,
            "searchFiltersActive": True
            if most_recent_search_results is not None
            else False,
        }

        return render(request, "index.html", context)
    return render(request, "index.html")


def search(request):
    global last_uploaded_csv_data
    global initial
    global headers
    global filename
    global most_recent_search_results

    # if last_uploaded_csv_data is None:
    #     print("Well???")
    #     return redirect("/")

    get_data = request.GET
    query = str(get_data["query"])
    print("query:", query)

    df = last_uploaded_csv_data
    json_string = df.to_json(orient="records")
    json_data = json.loads(json_string)
    # print("df:", df)

    # underscored_headers = df.columns.tolist()

    matching_frames = []
    for header in headers:
        if header == "Edit" or header == "Delete" or header == "Unique Index":
            continue
        # print(header)
        filtered_df = df.loc[df[header].str.contains(query, case=False)]
        # print("filtered:", filtered_df)
        matching_frames.append(filtered_df)
      
    print("matching_frame", matching_frames)

    result_frame = pd.concat(matching_frames, axis=0, ignore_index=True)
    result_frame = result_frame.drop_duplicates()
    json_string = result_frame.to_json(orient="records")
    json_data = json.loads(json_string)
    if len(result_frame) == 0:
        messages.error(request, 'No results found.')
        #  include popup saying no results or something
        return redirect("/")

    most_recent_search_results = json_data

    context = {
        "display_headers": headers,
        "data": json_data,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }

    return render(request, "index.html", context)


def custom_sort(col):
    try:
        # Try converting the values to numbers
        converted_values = [convert_to_valid_date(value) for value in col]
        return converted_values
    except ValueError:
        try:
            # If conversion fails, use the original method (str.lower())
            converted_values = [float(value) for value in col]
            return converted_values
        except ValueError:
            return col.str.lower()


def sortByHeader(request, header):
    print(header)
    global last_uploaded_csv_data
    global initial
    global headers
    global most_recent_search_results

    df = last_uploaded_csv_data
    header = header.replace("%2F", "/")
    print(df)

    if most_recent_search_results is not None:
        json_data = most_recent_search_results
        filtered_df = pd.DataFrame(json_data)
        df_sorted = filtered_df.sort_values(
            by=header, key=custom_sort, ascending=ascending[header]
        )
        ascending[header] = not ascending[header]
        json_string = df_sorted.to_json(orient="records")
        json_data = json.loads(json_string)
    else:
        df_sorted = df.sort_values(
            by=header, key=custom_sort, ascending=ascending[header]
        )
        ascending[header] = not ascending[header]
        last_uploaded_csv_data = df_sorted
        print(df_sorted)
        json_string = df_sorted.to_json(orient="records")
        json_data = json.loads(json_string)

    context = {
        "display_headers": headers,
        "data": json_data,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }
    return render(request, "index.html", context)


def clear_all(request):
    global last_uploaded_csv_data
    global initial
    global headers
    global filename
    global most_recent_search_results

    most_recent_search_results = None
    last_uploaded_csv_data = None
    initial = 0
    filename = ""
    headers = []

    return redirect("/")


def is_valid_date(date_string):
    try:
        # Attempt to parse the string into a date
        parsed_date = parser.parse(date_string)
        return True
    except ValueError:
        # If parsing fails, it's not a valid date
        return False


def is_valid_date_format(date_string):
    try:
        # Attempt to parse the date string using the specified format
        datetime.strptime(date_string, "%m/%d/%Y")
        return True
    except ValueError:
        # If parsing fails, the format is not valid
        return False


def convert_to_valid_date(date_string):
    try:
        # Attempt to parse the string into a date using the specified format
        parsed_date = datetime.strptime(date_string, "%m/%d/%Y")
        return parsed_date
    except ValueError:
        # If parsing fails, return None
        raise ValueError(f"Not a valid date")
