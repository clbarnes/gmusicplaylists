import billboard
import requests


def get_hot_100():
    chart = billboard.ChartData('hot-100')
    return [(entry.artist, entry.title) for entry in chart]


def get_top_40():
    chart = requests.get('http://www.ben-major.co.uk/labs/top40/api/singles').json()
    entries = chart['entries']
    queries = [(entry['artist'], entry['title']) for entry in entries]
    return queries