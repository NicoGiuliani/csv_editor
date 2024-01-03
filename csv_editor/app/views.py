import ast
from datetime import datetime
import json
from django.contrib.sessions.models import Session
import os
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponse
import pandas as pd
from dateutil import parser
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib import messages
import csv


def home(request, tabId=None):

    print("boooooooo:", tabId)
    df = None

    if tabId in request.session:
        current_session = request.session[tabId]
        # print(current_session)

        if "last_uploaded_csv_data" in current_session:
            df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
            print("loaded:", df)
        else:
            df = None

        if "initial" in current_session:
            initial = int(current_session["initial"])
        else:
            initial = 0

        if "headers" in current_session:
            headers = current_session["headers"]
            try:
                headers = ast.literal_eval(headers)
            except (SyntaxError, ValueError) as e:
                print(f"Error: {e}")
        else:
            headers = []

        if "filename" in current_session:
            filename = current_session["filename"]
        else:
            filename = ""

        if "most_recent_search_results" in current_session:
            most_recent_search_results = None
            current_session["most_recent_search_results"] = None
        
    context = {}

    if df is not None:
        json_object = df.to_json(orient="records")
        json_string = json.loads(json_object)

        context = {
            "display_headers": headers,
            "data": json_string,
            "initial": initial,
            "filename": filename,
            "searchFiltersActive": True
            if most_recent_search_results is not None
            else False,
        }

    return render(request, "index.html", context)




def export(request):

    if request.method == "POST":
        print("this")
        post_data = request.POST
        print(post_data)
        tabId = post_data.get("exportButton")
        current_session = request.session[tabId]

    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
    else:
        return redirect("/" + tabId)

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""

    # Specify the file path where you want to save the CSV file
    csv_file_path = "output_file.csv"

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


def delete(request, tabId, id):

    current_session = request.session[tabId]
    
    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
        # print(df)
    else:
        df = None

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""

    if "most_recent_search_results" in current_session:
        most_recent_search_results = current_session["most_recent_search_results"]
    else:
        most_recent_search_results = None

    df = df.drop(df[df["unique_index"] == int(id)].index)
    df = df.drop(df[df["unique_index"] == id].index)
    print("Deleted ID:", id)
    print("dropped:", df)

    # last_uploaded_csv_data = df

    # if most_recent_search_results is None:
    json_object = df.to_json(orient="records")
    json_string = json.loads(json_object)

    if most_recent_search_results is not None:
        print("filtered")
        df = pd.DataFrame(most_recent_search_results)
        df = df.drop(df[df["unique_index"] == int(id)].index)
        df = df.drop(df[df["unique_index"] == id].index)
        # print(df)
        new_json_object = df.to_json(orient="records")
        json_string = json.loads(new_json_object)
        most_recent_search_results = json_string
        
    # use this
    current_session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results

    request.session[tabId] = current_session

    if len(json_string) == 0:
            return redirect("/" + tabId)

    context = {
        "display_headers": headers,
        "data": json_string,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }
    return render(request, "index.html", context)


def edit(request, tabId, id):

    current_session = request.session[tabId]

    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
        print(df)
    else:
        df = None

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""

    if "most_recent_search_results" in current_session:
        most_recent_search_results = current_session["most_recent_search_results"]
    else:
        most_recent_search_results = None

    print("edit")
    print("id:", id)

    # this is made a string for now, may have to change later
    to_edit = df.loc[df["unique_index"] == int(id)]
    print(to_edit)

    # last_uploaded_csv_data = df
    json_object = df.to_json(orient="records")
    json_string = json.loads(json_object)

    to_edit_json_object = to_edit.to_json(orient="records")
    json_to_edit_string = json.loads(to_edit_json_object)
    # print(json_to_edit_string)

    if most_recent_search_results is not None:
        json_string = most_recent_search_results

    # use this
    current_session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results

    request.session[tabId] = current_session

    # print("edit:", current_session["last_uploaded_csv_data"])

    context = {
        "display_headers": headers,
        "data": json_string,
        "to_edit": json_to_edit_string[0],
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }
    return render(request, "index.html", context)


def create(request):

    if request.method == "POST":
        print("updating...")
        post_data = request.POST
        # print(post_data)
        tabId = post_data.get("create_and_edit")

    current_session = request.session[tabId]

    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
        print("loaded")
    else:
        df = None

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""


    most_recent_search_results = None

    post_data = request.POST
    new_data = {}

    for entry in post_data:
        if entry == "csrfmiddlewaretoken":
            continue
        new_data[entry] = post_data.get(entry)

    new_data["unique_index"] = int(new_data["unique_index"])
    print("new_data:", new_data)

    new_data_df = pd.DataFrame([new_data])
    df = pd.concat([df, new_data_df], ignore_index=True)

    json_object = df.to_json(orient="records")
    json_string = json.loads(json_object)

    print("json_data:", json_string)
    initial += 1

    # use this
    current_session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results

    request.session[tabId] = current_session

    context = {
        "data": json_string,
        "display_headers": headers,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }

    return render(request, "index.html", context)


def update(request):

    if request.method == "POST":
        print("updating...")
        post_data = request.POST
        # print(post_data)
        tabId = post_data.get("create_and_edit")

    current_session = request.session[tabId]

    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
        # print(df)
    else:
        df = None

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""

    if "most_recent_search_results" in current_session:
        most_recent_search_results = current_session["most_recent_search_results"]
    else:
        most_recent_search_results = None


    new_data = {}

    for entry in post_data:
        if entry == "csrfmiddlewaretoken":
            continue
        new_data[entry] = post_data.get(entry)


    i = new_data["unique_index"]
    underscored_headers = df.columns.tolist()
    json_object = df.to_json(orient="records")
    json_string = json.loads(json_object)

    df.loc[df["unique_index"] == int(i), underscored_headers] = list(
        map(lambda x: new_data[x], underscored_headers)
    )
    df.loc[df["unique_index"] == i, "unique_index"] = int(i)

    json_object = df.to_json(orient="records")
    json_string = json.loads(json_object)

    if most_recent_search_results is not None:
        df = pd.DataFrame(json.loads(most_recent_search_results))
        df.loc[df["unique_index"] == int(i), underscored_headers] = list(
            map(lambda x: new_data[x], underscored_headers)
        )
        df.loc[df["unique_index"] == i, "unique_index"] = int(i)
        json_object = df.to_json(orient="records")
        json_string = json.loads(json_object)
        most_recent_search_results = json_string

    # use this
    current_session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results

    request.session[tabId] = current_session

    print("df:", df)

    context = {
        "data": json_string,
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
    print("ok")

    post_data = request.POST
    tabId = post_data.get("tabId")

    print(tabId)

    most_recent_search_results = None

    current_session = {}
    current_session["most_recent_search_results"] = most_recent_search_results

    data_file = request.FILES["csvFile"]
    filename = data_file
    print("name:", data_file)
    filetype = filename.name.split(".")[1]

    df = pd.read_csv(data_file) if filetype == "csv" else pd.read_excel(data_file)

    json_string = df.to_json(orient="records")
    json_data = json.loads(json_string)

    headers = df.columns.tolist()

    final_data = []
    initial = 0
    ascending = None
    for entry in json_data:
        dictionary = {"unique_index": initial}
        initial += 1
        ascending = {}
        for header in headers:
            ascending[header] = True
            dictionary[header] = str(entry[header])
        final_data.append(dictionary)

    headers.insert(0, "Unique Index")
    headers.insert(0, "Delete")
    headers.insert(0, "Edit")

    new_df = pd.DataFrame(final_data)
    json_object = new_df.to_json(orient="records")
    json_string = json.loads(json_object)

    ascending = json.dumps(ascending)
    # print("type2:", type(ascending))


    # use this
    current_session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results
    current_session["ascending"] = ascending

    request.session[tabId] = current_session

    context = {
        "display_headers": headers,
        "data": json_string,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }

    return render(request, "index.html", context)


def search(request):
    print("search")
    post_data = request.GET
    print(post_data)
    tabId = post_data.get("searchButton")
    current_session = request.session[tabId]

    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
    else:
        df = None

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""

    if "most_recent_search_results" in current_session:
        current_session["most_recent_search_results"] = None

    get_data = request.GET
    query = str(get_data["query"])
    print("query:", query)

    json_object = df.to_json(orient="records")
    json_string = json.loads(json_object)
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
    json_object = result_frame.to_json(orient="records")
    json_string = json.loads(json_object)
    if len(result_frame) == 0:
        messages.error(request, 'No results found.')
        #  include popup saying no results or something
        return redirect("/" + tabId)

    most_recent_search_results = json_string

    # use this
    # request.session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results

    request.session[tabId] = current_session

    context = {
        "display_headers": headers,
        "data": json_string,
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


def sortByHeader(request, tabId, header):
    current_session = request.session[tabId]

    if "last_uploaded_csv_data" in current_session:
        df = pd.DataFrame(json.loads(current_session["last_uploaded_csv_data"]))
        print(df)
    else:
        df = None

    if "initial" in current_session:
        initial = int(current_session["initial"])
    else:
        initial = 0

    if "headers" in current_session:
        headers = current_session["headers"]
        try:
            headers = ast.literal_eval(headers)
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
    else:
        headers = []

    if "filename" in current_session:
        filename = current_session["filename"]
    else:
        filename = ""

    if "most_recent_search_results" in current_session:
        most_recent_search_results = current_session["most_recent_search_results"]
    else:
        most_recent_search_results = None

    if "ascending" in current_session:
        ascending = current_session["ascending"]
        ascending = json.loads(ascending.replace("'", "\""))
        print("asc", type(ascending))

    header = header.replace("%2F", "/")

    if most_recent_search_results is not None:
        filtered_df = pd.DataFrame(most_recent_search_results)
        df_sorted = filtered_df.sort_values(
            by=header, key=custom_sort, ascending=ascending[header]
        )
        ascending[header] = not ascending[header]
        json_object = df_sorted.to_json(orient="records")
        json_string = json.loads(json_object)
    else:
        df_sorted = df.sort_values(
            by=header, key=custom_sort, ascending=ascending[header]
        )
        ascending[header] = not ascending[header]
        print(df_sorted)
        json_object = df_sorted.to_json(orient="records")
        json_string = json.loads(json_object)


    ascending = json.dumps(ascending)

    # use this
    current_session["last_uploaded_csv_data"] = json_object
    current_session["initial"] = str(initial)
    current_session["headers"] = str(headers)
    current_session["filename"] = str(filename)
    current_session["most_recent_search_results"] = most_recent_search_results
    current_session["ascending"] = ascending

    request.session[tabId] = current_session

    context = {
        "display_headers": headers,
        "data": json_string,
        "initial": initial,
        "filename": filename,
        "searchFiltersActive": True
        if most_recent_search_results is not None
        else False,
    }
    return render(request, "index.html", context)


def clear_all(request):
    # use this
    request.session.clear()
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
