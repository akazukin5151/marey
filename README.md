# marey

A python script that scrapes [ekitan](ekitan.com/) (a Japanese transportation routing service) to make a train schedule diagram

Note that the following scripts will immediately return if their output file already exists (regardless if the file is correct)
- get_urls.py
- downloads.py (Checks if every file to be downloaded already exists)
- scrap_html.py

To force the scripts to run, delete their output files

# Install dependencies

Install the dependencies with your favourite package manager:
- BeautifulSoup
- pandas
- matplotlib
- numpy
- Python 3 (obviously)

# Running

Either edit main.py in this section to use your own url and line name

```py
    url = 'https://ekitan.com/timetable/railway/line-station/180-0/d1?dt=20211101'
    line_name = 'chuo'
    main(url, line_name)
```

Or from another python module, import `main` and call `main.main(url, line_name)`, giving your own `url` and `line_name`

# See also
- https://mbtaviz.github.io/
