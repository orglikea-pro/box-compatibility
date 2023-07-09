from math import floor
import json
import argparse


def check_compatility_easy(outer_x, outer_y, inner_x, inner_y):
    result = []

    # check if the inner box is larger that the outer
    if inner_x > outer_x or inner_y > outer_y:
        return {"total_count": 0}

    count_full_x = outer_x / inner_x
    count_full_y = outer_y / inner_y

    count_x = floor(count_full_x)
    count_y = floor(count_full_y)

    inner_area = outer_x * outer_y
    user_area = (count_x * inner_x) * (count_y * inner_y)
    user_area_percent = user_area / inner_area

    return {
        "x_count": count_x,
        "x_diff": count_full_x % 1,
        "y_count": count_y,
        "y_diff": count_full_y % 1,
        "total_count": floor(count_full_x) * floor(count_full_y),
        "used_area_percent": user_area_percent,
    }


def check_compatility(outer_x, outer_y, inner_x, inner_y):
    # Check horizontal and vertical
    horizontal = check_compatility_easy(outer_x, outer_y, inner_x, inner_y)
    vertical = check_compatility_easy(outer_x, outer_y, inner_y, inner_x)

    if horizontal["total_count"] > vertical["total_count"]:
        return horizontal
    else:
        return vertical


def render_to_html(items, prefix="<html><body>", postfix="</body></html>"):
    result = prefix
    # Headline (no shelfs)
    ct = 1
    result += "<table><tr class='boxcomp-header'>"
    result += "<th>Outer\\Inner</th>"
    for inner_box in items:
        if inner_box["type"] == "Container":
            ct = ct + 1
            result += (
                "<th>" + inner_box["vendor"] + "<br />" + inner_box["name"] + "</th>"
            )
    result += "</tr>"

    # for each box or shelf, create a row for each non shelf
    for outer_box in items:
        result += (
            "<tr class='boxcomp-row'><td>"
            + outer_box["vendor"]
            + "<br /><a href='"
            + outer_box["link"]
            + "'>"
            + outer_box["name"]
            + "</a><br /><small>"
            + outer_box["type"]
            + "</small></td>"
        )
        for inner_box in items:
            # Just non Shelfs because shelfs in shelfs make not sense
            if inner_box["type"] == "Container":
                result += "<td class='boxcomp-state'>" + (
                    check_and_render_compatility_to_html(
                        outer_box["inner_x"],
                        outer_box["inner_y"],
                        inner_box["outer_x"],
                        inner_box["outer_y"],
                    )
                    + "</td>"
                )
        result += "</tr>"
    result += "</table>"
    result += "<h2>Legend</h2>\n" \
        "❌ No fit at all <br />\n" \
        "🔘 Bad fit (<70%% surface utilization) <br /> \n" \
        "✔️ Good fit (>70%% fit)"
    result += postfix
    return result


def render_to_md(items, prefix="# Box Compatibliy\n"):
    result = prefix
    # Headline (no shelfs)
    ct = 1
    result += "| Outer\\Inner|"
    for inner_box in items:
        if inner_box["type"] == "Container":
            ct = ct + 1
            result += inner_box["vendor"] + "<br />" + inner_box["name"] + "|"
    result += "\n"
    # write the | --- | based on the non shelfs
    result += "| --- " * ct + "|\n"

    # for each box or shelf, create a row for each non shelf
    for outer_box in items:
        result += "|{vendor}[<br />{name}]({link})<br />*{type}* |".format(**outer_box)
        for inner_box in items:
            # Just non Shelfs because shelfs in shelfs make not sense
            if inner_box["type"] == "Container":
                result += (
                    check_and_render_compatility_to_html(
                        outer_box["inner_x"],
                        outer_box["inner_y"],
                        inner_box["outer_x"],
                        inner_box["outer_y"],
                    )
                    + " | "
                )
        result += "|\n" 
    result += "  \n" \
            "## Legend\n" \
            "❌ No fit at all  \n" \
            "🔘 Bad fit (<70%% surface utilization)  \n" \
            "✔️ Good fit (>70%% fit)"
    return result


def check_and_render_compatility_to_html(outer_x, outer_y, inner_x, inner_y):
    compatility = check_compatility(outer_x, outer_y, inner_x, inner_y)

    if compatility["total_count"] == 0:
        return "❌"
    else:
        icon = ""
        if compatility["used_area_percent"] < 0.7:
            icon = "🔘"
        else:
            icon = "✔️"

        return "{}<br /><small>~{:.0f}%</small><br />{} <small>({}x{})</small>".format(
            icon,
            compatility["used_area_percent"] * 100,
            compatility["x_count"] * compatility["y_count"],
            compatility["x_count"],
            compatility["y_count"],
        )


def load_data(filename):
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse and render box compatiblity.")
    parser.add_argument(
        "--format", help="Format to render. html, or md possible", default="md"
    )
    parser.add_argument("--input", help="Input Json file", default="data.json")
    parser.add_argument("--output", help="Input Json file", default=None)

    args = parser.parse_args()
    config = vars(args)

    boxdata = load_data(config["input"])

    content = ""
    output_filename = ""

    if config["format"] == "md":
        content = render_to_md(boxdata)
        output_filename = "output.md"

    if config["format"] == "html":
        content = render_to_html(boxdata)
        output_filename = "output.html"

    if config["output"] != None:
        output_filename = config["output"]

    with open(output_filename, "w", encoding="UTF-8") as f:
        f.write(content)
