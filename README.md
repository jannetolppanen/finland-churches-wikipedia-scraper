# Finnish Churches Coordinate Extractor

This project scrapes location information (latitude, longitude, and address) from Wikipedia pages of churches in Finland.

## Features

- Extracts coordinates and addresses from Wikipedia pages of Finnish churches
- Handles multiple coordinate formats
- Supports Catholic, Orthodox, and Lutheran churches
- Generates interactive maps and statistics

## Project Structure

```
.
├── coordinate_extractor.py       # Main extraction logic
├── run_extractor.py              # Single church type processing script
├── batch_process.py              # Process all church types
├── visualize_churches.py         # Create maps and statistics
├── output/                       # Output directory for JSON files and visualizations
```

## Prerequisites

Install the required packages:

```bash
pip install requests beautifulsoup4 folium pandas matplotlib
```

## Usage

### 1. Process only Catholic churches

```bash
python run_extractor.py
```

### 2. Process all church types (Catholic, Orthodox, Lutheran)

```bash
python batch_process.py
```

### 3. Visualize the churches on a map

```bash
python visualize_churches.py
```

This will generate:
- An interactive HTML map in `output/finnish_churches_map.html`
- Statistical graphs in `output/statistics/`

## Coordinate Extraction Methods

The extractor uses three different methods to find coordinates on Wikipedia pages:

1. From a span with id="coordinatespan" in the main content
2. From the mw-indicator with id="mw-indicator-AA-coordinates"
3. From the infobox table coordinates row

## Output

The script produces JSON files with the following structure:

```json
[
  {
    "name": "Church Name",
    "type": "Catholic",
    "wikipedia_link": "https://fi.wikipedia.org/wiki/Church_Name",
    "coordinates": {
      "lat": 60.123456,
      "lon": 24.789012,
      "format": "DMS",
      "original": "60°12′34.56″N, 24°78′90.12″E"
    },
    "address": "Church Street 1, 00100 Helsinki"
  },
  ...
]
```

## Notes

- The script includes random delays between requests to avoid overwhelming Wikipedia's servers
- It handles errors gracefully and logs issues it encounters
- Address extraction may not be successful for all churches

## License

This project is licensed under the MIT License - see the LICENSE file for details.
