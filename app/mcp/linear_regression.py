from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LinearRegressionMCP")


@mcp.tool()
def build_fit_line_for_all_zones() -> dict:
    """Builds a fit line for all zones."""
    x_data = {"A": [], "B": [], "C": [], "D": []}
    y_data = {"A": [], "B": [], "C": [], "D": []}

    from app.mcp.trend_analyzer import get_traffic_trends

    trends = get_traffic_trends()
    for entry in trends:
        ts = entry.get("timestamp")
        z = entry.get("zone")
        count = entry.get("count", 0)
        if ts and z in x_data:
            minutes = int(ts.split(":")[0]) * 60 + int(ts.split(":")[1])
            x_data[z].append(float(minutes))
            y_data[z].append(float(count))

    if not any(x_data.values()) or not any(y_data.values()):
        raise ValueError("No data found for zones")

    # perform minutes normalization [min_current - min_start]
    for z in x_data:
        min_start = min(x_data[z])
        min_end = max(x_data[z])
        x_data[z] = [(x - min_start) / (min_end - min_start) for x in x_data[z]]
    if not any(x_data.values()) or not any(y_data.values()):
        raise ValueError("No data found for zones")

    fit_lines = {}
    for zone in x_data:
        if len(x_data[zone]) >= 2:
            fit_lines[zone] = simple_linear_regression(x_data[zone], y_data[zone])
        else:
            fit_lines[zone] = {"slope": 0.0, "intercept": 0.0}
    return fit_lines


def simple_linear_regression(x: list[float], y: list[float]) -> dict:
    """Performs simple linear regression and returns the slope and intercept.

    Args:
        x: A list of independent variable values.
        y: A list of dependent variable values.

    Returns:
        A dictionary containing the 'slope' and 'intercept' of the regression line.
    """
    if len(x) != len(y) or len(x) < 2:
        raise ValueError(
            "Input lists must have the same length and at least two elements."
        )

    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y, strict=True))
    sum_x_sq = sum(xi**2 for xi in x)

    # Calculate slope (m)
    numerator = n * sum_xy - sum_x * sum_y
    denominator = n * sum_x_sq - sum_x**2

    if denominator == 0:
        raise ValueError("Cannot perform regression: all x values are the same.")

    slope = numerator / denominator

    # Calculate intercept (b)
    intercept = (sum_y - slope * sum_x) / n
    mse = (
        sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y, strict=True))
        / n
    )
    return {"slope": slope, "intercept": intercept, "mse": mse}


if __name__ == "__main__":
    mcp.run()
